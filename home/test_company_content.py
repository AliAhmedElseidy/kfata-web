from io import StringIO
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from wagtail.models import Page
from home.models import HomePage, ContentPage, PresentationUpdate
from home.management.commands.enrich_company_content import load_pack

class CompanyContentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_content', stdout=StringIO())
        call_command('import_profile_drafts', stdout=StringIO())
    def run_update(self, **kwargs):
        output = StringIO()
        call_command('enrich_company_content', stdout=output, **kwargs)
        return output.getvalue()
    def test_pack_has_sources_both_languages_and_missing_project_types(self):
        pack = load_pack()
        self.assertEqual(len(pack['pages']),39)
        self.assertEqual(sum(p['kind']=='project' for p in pack['pages']),24)
        for slug in ['anb-jeddah-head-office','anb-internal-clinic','anb-control-room','anb-tower-cafe','garage-finishing','road-blocker-installations','parking-shades']:
            self.assertIn(slug,[p['slug'] for p in pack['pages']])
        self.assertNotIn('anb-golden-belt',[p['slug'] for p in pack['pages']])
    def test_preview_writes_nothing(self):
        before=list(Page.objects.values_list('pk','latest_revision_id'))
        markers=PresentationUpdate.objects.count()
        self.assertIn('PREVIEW ONLY', self.run_update())
        self.assertEqual(before,list(Page.objects.values_list('pk','latest_revision_id')))
        self.assertEqual(markers,PresentationUpdate.objects.count())
    def test_publication_requires_apply(self):
        with self.assertRaises(CommandError): self.run_update(publish=True)
    def test_updates_body_relations_and_bilingual_new_pages(self):
        self.run_update(apply=True,publish=True)
        ar=ContentPage.objects.get(slug='road-works',locale__language_code='ar')
        self.assertTrue(ar.live)
        self.assertIn('أرصفة',ar.body[0].value['text'].source)
        clinic=ContentPage.objects.get(slug='anb-internal-clinic',locale__language_code='ar')
        english=clinic.get_translation_or_none(HomePage.objects.get(slug='en').locale)
        self.assertIsNotNone(english);self.assertTrue(english.live)
        self.assertEqual(clinic.location,'المنطقة الشرقية')
        self.assertTrue(clinic.scope)
        self.assertTrue(clinic.related_sectors.filter(slug='banking').exists())
        self.assertTrue(clinic.related_services.filter(slug='renovation').exists())
        self.assertEqual(self.client.get('/ar/projects/anb-internal-clinic/').status_code,200)
        self.assertEqual(self.client.get('/en/projects/anb-internal-clinic/').status_code,200)
    def test_editor_draft_and_home_are_preserved(self):
        owner=get_user_model().objects.create_superuser('content-owner','owner@example.test','test-only')
        p=ContentPage.objects.get(slug='anb-new-tower',locale__language_code='en')
        p.summary='Owner draft';revision=p.save_revision(user=owner)
        home=HomePage.objects.get(slug='ar');before=(home.headline,home.latest_revision_id)
        self.run_update(apply=True,publish=True)
        p.refresh_from_db();home.refresh_from_db()
        self.assertEqual(p.latest_revision_id,revision.pk)
        self.assertEqual(home.latest_revision_id,before[1]);self.assertEqual(home.headline,before[0])
    def test_repeat_does_not_restore_cleared_body_or_renamed_page(self):
        self.run_update(apply=True,publish=True)
        p=ContentPage.objects.get(slug='anb-internal-clinic',locale__language_code='ar')
        p.slug='clinic-review';p.body=[];p.save_revision().publish()
        count=Page.objects.count()
        self.run_update(apply=True,publish=True)
        p.refresh_from_db();self.assertFalse(p.body)
        self.assertEqual(Page.objects.count(),count)
        self.assertFalse(ContentPage.objects.filter(slug='anb-internal-clinic',locale__language_code='ar').exists())
    def test_draft_mode_does_not_publish_existing_or_new_content(self):
        p=ContentPage.objects.get(slug='road-works',locale__language_code='ar')
        self.assertFalse(p.live)
        self.run_update(apply=True)
        p.refresh_from_db();self.assertFalse(p.live)
        self.assertFalse(ContentPage.objects.get(slug='garage-finishing',locale__language_code='ar').live)

    def test_curated_layout_blocks_survive_enrichment(self):
        p=ContentPage.objects.get(slug='contracting',locale__language_code='ar')
        p.body=[('heading',{'visible':True,'tone':'dark','title':'Old source copy','text':'<p>Old text</p>'}),('faq',{'visible':True,'tone':'stone','title':'Curated questions','items':[{'question':'Question','answer':'Answer'}]})]
        p.save_revision().publish()
        self.run_update(apply=True,publish=True)
        p.refresh_from_db()
        self.assertEqual(p.body[0].value['tone'],'dark')
        self.assertNotIn('Old text',p.body[0].value['text'].source)
        self.assertEqual(p.body[1].block_type,'faq')
        self.assertEqual(p.body[1].value['title'],'Curated questions')

    def test_public_listing_paginates_every_case_and_relations_are_navigable(self):
        self.run_update(apply=True,publish=True)
        for lang in ['ar','en']:
            seen=set()
            response=self.client.get(f'/{lang}/projects/')
            photos=[p for p in response.context['items'] if p.hero_image_id]
            if photos:
                self.assertTrue(response.context['items'][0].hero_image_id)
            for number in range(1,response.context['items'].paginator.num_pages+1):
                result=self.client.get(f'/{lang}/projects/',{'page':number})
                self.assertEqual(result.status_code,200)
                for page in result.context['items']:
                    seen.add(page.slug)
                    self.assertContains(result,page.url)
            expected={p['slug'] for p in load_pack()['pages'] if p['kind']=='project'}
            self.assertTrue(expected.issubset(seen))
            clinic=self.client.get(f'/{lang}/projects/anb-internal-clinic/')
            self.assertContains(clinic,f'/{lang}/services/renovation/')
            self.assertContains(clinic,f'/{lang}/sectors/banking/')
            self.assertContains(self.client.get(f'/{lang}/sectors/banking/'),f'/{lang}/projects/')

    def test_sector_filter_uses_relationship_without_rewriting_project_facts(self):
        self.run_update(apply=True,publish=True)
        for lang in ['ar','en']:
            sector=ContentPage.objects.get(locale__language_code=lang,slug='banking')
            tower=ContentPage.objects.get(locale__language_code=lang,slug='anb-new-tower')
            old_label=tower.sector
            response=self.client.get(f'/{lang}/projects/',{'sector':sector.title})
            total=response.context['items'].paginator.count
            self.assertEqual(total,ContentPage.objects.live().public().filter(kind='project',locale=sector.locale,related_sectors=sector).count())
            self.assertEqual(response.context['sectors'].count(sector.title),1)
            self.assertContains(response,'&amp;sector=')
            tower.refresh_from_db();self.assertEqual(tower.sector,old_label)
