"""Safely stage 2026 KFATA brochure photos and bilingual editorial additions.

Do not run without an approved asset bundle. Preview is the default; only
--apply writes, and only --apply --publish makes eligible content public.
The PDF, certificates and third-party logos never enter the public importer.
"""
import hashlib
import json
import re
from collections import Counter, defaultdict
from html import escape
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from PIL import Image
from wagtail.images import get_image_model

from home.models import ContentPage, HomePage, ImportedImage, PresentationUpdate

PACK_FILE = Path(__file__).resolve().parents[2] / "content" / "kfata_2026_additions.json"
PHOTO_FILE = PACK_FILE.with_name("kfata_2026_photos.json")
ASSET_DIR = Path(settings.BASE_DIR) / "assets" / "source-2026"
SOURCE_MARK = "kfata26-"
KNOWN_IMAGE = re.compile(r"^[a-z][a-z0-9-]+-\d{2}\.webp$")
MAX_IMAGE_SIZE = 6 * 1024 * 1024


def load_source_pack():
    pack = json.loads(PACK_FILE.read_text(encoding="utf-8"))
    if not pack.get("pages") or not pack.get("photo_groups"):
        raise CommandError("Incomplete 2026 profile pack.")
    seen = set()
    for item in pack["pages"]:
        if item["kind"] not in {"page", "service", "project"}:
            raise CommandError("Invalid content kind.")
        key = (item["parent"], item["slug"])
        if key in seen:
            raise CommandError("Duplicate page slug.")
        seen.add(key)
        for lang in ("ar", "en"):
            if not all(item[lang].get(x) for x in ("title", "summary", "body")):
                raise CommandError("Incomplete language copy: " + item["slug"])
    return pack


def staged_photos(directory, reviews, allowed_groups):
    result = defaultdict(list)
    digests = set()
    if not directory.is_dir():
        return result
    for path in sorted(directory.iterdir()):
        if not path.is_file() or not KNOWN_IMAGE.fullmatch(path.name):
            continue
        group = path.stem.rsplit("-", 1)[0]
        if group not in allowed_groups or path.name not in reviews:
            raise CommandError("Unreviewed image: " + path.name)
        if path.stat().st_size > MAX_IMAGE_SIZE:
            raise CommandError("Image exceeds 6 MB limit: " + path.name)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != reviews[path.name]["sha256"]:
            raise CommandError("Image checksum differs from the reviewed file: " + path.name)
        if digest in digests:
            raise CommandError("Duplicate image: " + path.name)
        digests.add(digest)
        with Image.open(path) as image:
            if image.format != "WEBP" or image.width * image.height > 4_000_000:
                raise CommandError("Invalid WebP: " + path.name)
            image.load()
        result[group].append(path)
    return result



def locked_by_editor(page):
    revision = page.get_latest_revision()
    return bool((revision and revision.user_id) or page.revisions.filter(user__isnull=False).exists()
                or (page.live and page.has_unpublished_changes))


class Command(BaseCommand):
    help = "Stage new KFATA brochure copy and photos; preview by default, --apply then --publish."

    def add_arguments(self, parser):
        parser.add_argument("--asset-dir", type=Path, help="Directory containing reviewed WebP files.")
        parser.add_argument("--apply", action="store_true", help="Import images and save editorial drafts.")
        parser.add_argument("--publish", action="store_true", help="Publish eligible updates; requires --apply.")

    @transaction.atomic
    def handle(self, **options):
        if options["publish"] and not options["apply"]:
            raise CommandError("--publish requires --apply.")
        pack = load_source_pack()
        reviews = json.loads(PHOTO_FILE.read_text(encoding="utf-8"))
        files = staged_photos(options["asset_dir"] or ASSET_DIR, reviews, pack["photo_groups"])
        homes = {lang: HomePage.objects.filter(locale__language_code=lang).first() for lang in ("ar", "en")}
        if any(home is None for home in homes.values()):
            raise CommandError("The existing bilingual home pages must exist. Never seed/reset production.")
        if options["apply"] and not files:
            raise CommandError("No source images found. Extract the supplied media bundle into assets/source-2026/.")
        summary = Counter()
        images = defaultdict(list)

        # Import only images that an eligible project can use.
        def group_images(group):
            if group not in images:
                for path in files[group]:
                    key = SOURCE_MARK + path.stem
                    record = ImportedImage.objects.filter(source_key=key).select_related("image").first()
                    if record and not record.image_id:
                        raise CommandError("An editor removed the source image: " + path.name)
                    if record:
                        image = record.image
                        summary["images preserved"] += 1
                    else:
                        with path.open("rb") as stream:
                            image = get_image_model().objects.create(
                                title=reviews[path.name]["en"],
                                file=File(stream, name="kfata-2026-" + path.name),
                            )
                        ImportedImage.objects.create(source_key=key, image=image)
                        summary["images imported"] += 1
                    images[group].append((image, reviews[path.name]))
            return images[group]

        # Pages first so a freshly created Al Wadi project can receive its gallery.
        new_projects = set()
        pending_projects = set()
        for item in pack["pages"]:
            parents = {}
            existing = {}
            for lang, root in homes.items():
                parent = ContentPage.objects.child_of(root).filter(slug=item["parent"]).first() if item["parent"] else root
                if parent and parent.live and not parent.get_view_restrictions().exists():
                    parents[lang] = parent
                    page = ContentPage.objects.child_of(parent).filter(slug=item["slug"]).first()
                    if page:
                        existing[lang] = page
            first_page = next(iter(existing.values()), None)
            for lang, root in homes.items():
                parent = parents.get(lang)
                locale = root.locale
                if not parent:
                    summary["missing or nonpublic parent"] += 1
                    continue
                page = existing.get(lang)
                if page and locked_by_editor(page):
                    summary["editor draft preserved"] += 1
                    first_page = first_page or page
                    continue
                if page:
                    # Existing editorial pages are not overwritten by source additions.
                    summary["existing page preserved"] += 1
                    first_page = first_page or page
                    continue
                if not options["apply"]:
                    summary["would create page"] += 1
                    if item["kind"] == "project":
                        pending_projects.add((item["slug"], lang))
                    continue
                copy = item[lang]
                page = ContentPage(
                    title=copy["title"], slug=item["slug"], locale=locale,
                    kind=item["kind"], live=False, summary=copy["summary"],
                    search_description=copy["summary"][:160],
                    show_in_menus=not item.get("review_only", False),
                )
                if first_page:
                    page.translation_key = first_page.translation_key
                parent.add_child(instance=page)
                sections = [{"title": copy["title"], "body": copy["body"]}, *copy.get("sections", [])]
                page.body = [
                    ("heading", {
                        "visible": True, "tone": "stone", "eyebrow": "",
                        "title": section["title"],
                        "text": "<p>" + escape(section["body"]) + "</p>",
                    })
                    for section in sections
                ]
                for field in ("services", "sectors"):
                    targets = ContentPage.objects.live().public().filter(
                        slug__in=item.get(field, []), locale=locale, kind=field[:-1],
                    )
                    getattr(page, "related_" + field).add(*targets)
                revision = page.save_revision()
                if options["publish"] and not item.get("review_only", False):
                    revision.publish()
                else:
                    page.live = False
                    page.save(update_fields=["live"])
                first_page = first_page or page
                summary["new pages saved"] += 1
                if item["kind"] == "project":
                    new_projects.add((page.slug, lang))

        for group, slug in pack["photo_groups"].items():
            if not files.get(group):
                summary["group missing files"] += 1
                continue
            for lang in ("ar", "en"):
                project_index = ContentPage.objects.child_of(homes[lang]).filter(slug="projects").first()
                page = ContentPage.objects.child_of(project_index).filter(
                    slug=slug, locale=homes[lang].locale, kind="project",
                ).first() if project_index else None
                if not page:
                    if (slug, lang) in pending_projects:
                        summary["would attach gallery"] += 1
                    else:
                        summary["project not found"] += 1
                    continue
                marker = "kfata-2026-photo-v1:" + group + ":" + lang
                if PresentationUpdate.objects.filter(page=page, key=marker).exists():
                    summary["previously attached"] += 1
                    continue
                if (not page.live and not ((slug, lang) in new_projects and not options["publish"])
                        or locked_by_editor(page)
                        or not ContentPage.objects.public().filter(pk=page.pk).exists()):
                    summary["editor draft or restricted project preserved"] += 1
                    continue
                if not options["apply"]:
                    summary["would attach gallery"] += 1
                    continue
                selected = group_images(group)
                block_title = "صور المشروع" if lang == "ar" else "Project photographs"
                # Retain the IDs and structure of existing editorial blocks.
                previous = page.body.get_prep_value()
                new_block = page.body.stream_block.to_python([{
                    "type": "gallery",
                    "value": {
                        "visible": True, "tone": "stone", "title": block_title,
                        "images": [
                            {"image": image.pk, "caption": "", "alt": review[lang]}
                            for image, review in selected
                        ],
                    },
                }])
                page.body = previous + new_block.get_prep_value()
                if page.hero_image_id is None:
                    page.hero_image = selected[0][0]
                revision = page.save_revision()
                if options["publish"] and page.live:
                    revision.publish()
                PresentationUpdate.objects.create(page=page, key=marker)
                summary["galleries attached"] += 1

        summary["reviewed WebPs available"] = sum(map(len, files.values()))
        prefix = "APPLIED" if options["apply"] else "PREVIEW ONLY — no database changes"
        self.stdout.write(prefix + ": " + ", ".join(
            str(summary[key]) + " " + key for key in sorted(summary)
        ))
