"""Safely stage 2026 KFATA brochure photos and bilingual editorial additions.

Do not run without an approved asset bundle. Preview is the default; only
--apply writes, and only --apply --publish makes eligible content public.
The PDF, certificates and third-party logos never enter the public importer.
"""
import json
import re
from collections import Counter, defaultdict
from html import escape
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from wagtail.images import get_image_model
from wagtail.models import Locale

from home.models import ContentPage, HomePage, ImportedImage, PresentationUpdate

PACK_FILE = Path(__file__).resolve().parents[2] / "content" / "kfata_2026_additions.json"
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


def staged_photos():
    result = defaultdict(list)
    if not ASSET_DIR.is_dir():
        return result
    for path in sorted(ASSET_DIR.iterdir()):
        if not path.is_file() or not KNOWN_IMAGE.fullmatch(path.name):
            continue
        if path.stat().st_size > MAX_IMAGE_SIZE:
            raise CommandError("Image exceeds 6 MB limit: " + path.name)
        group = path.stem.rsplit("-", 1)[0]
        result[group].append(path)
    return result


def locked_by_editor(page):
    revision = page.get_latest_revision()
    return bool((revision and revision.user_id) or (page.live and page.has_unpublished_changes))


class Command(BaseCommand):
    help = "Stage new KFATA brochure copy and photos; preview by default, --apply then --publish."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true", help="Import images and save editorial drafts.")
        parser.add_argument("--publish", action="store_true", help="Publish eligible updates; requires --apply.")

    @transaction.atomic
    def handle(self, **options):
        if options["publish"] and not options["apply"]:
            raise CommandError("--publish requires --apply.")
        pack = load_source_pack()
        files = staged_photos()
        homes = {lang: HomePage.objects.filter(locale__language_code=lang).first() for lang in ("ar", "en")}
        if any(home is None for home in homes.values()):
            raise CommandError("The existing bilingual home pages must exist. Never seed/reset production.")
        if options["apply"] and not files:
            raise CommandError("No source images found. Extract the supplied media bundle into assets/source-2026/.")
        summary = Counter()
        images = defaultdict(list)
        allowed_groups = set(pack["photo_groups"]) | set(pack["review_only_photo_groups"])
        for group, paths in files.items():
            if group not in allowed_groups:
                summary["unknown image group skipped"] += len(paths)
                continue
            for path in paths:
                key = SOURCE_MARK + path.stem
                record = ImportedImage.objects.filter(source_key=key).select_related("image").first()
                if not options["apply"]:
                    summary["already imported" if record and record.image_id else "would import"] += 1
                    continue
                image = record.image if record else None
                if image is None:
                    with path.open("rb") as stream:
                        image = get_image_model().objects.create(
                            title="KFATA | " + group.replace("-", " ") + " | source " + path.stem,
                            file=File(stream, name="kfata-2026-" + path.name),
                        )
                    ImportedImage.objects.update_or_create(source_key=key, defaults={"image": image})
                    summary["images imported"] += 1
                else:
                    summary["images preserved"] += 1
                images[group].append(image)

        # Pages first so a freshly created Al Wadi project can receive its gallery.
        for item in pack["pages"]:
            first_page = None
            for lang in ("ar", "en"):
                root = homes[lang]
                locale = Locale.objects.filter(language_code=lang).first()
                if item["parent"]:
                    parent = ContentPage.objects.child_of(root).filter(slug=item["parent"]).first()
                else:
                    parent = root
                if not parent or not locale:
                    summary["missing parent/locale"] += 1
                    continue
                page = ContentPage.objects.child_of(parent).filter(slug=item["slug"]).first()
                if locked_by_editor(page) if page else False:
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
                    continue
                copy = item[lang]
                page = ContentPage(
                    title=copy["title"], slug=item["slug"], locale=locale,
                    kind=item["kind"], live=False, summary=copy["summary"],
                    search_description=copy["summary"][:160],
                )
                if first_page:
                    page.translation_key = first_page.translation_key
                parent.add_child(instance=page)
                page.body = [("heading", {
                    "visible": True, "tone": "stone", "eyebrow": "KFATA",
                    "title": copy["title"],
                    "text": "<p>" + escape(copy["body"]) + "</p>",
                })]
                revision = page.save_revision()
                # Partner logos and certificates are deliberately not auto-published.
                if options["publish"] and page.slug != "clients-partners":
                    revision.publish()
                else:
                    page.live = False
                    page.save(update_fields=["live"])
                first_page = first_page or page
                summary["new pages saved"] += 1

        for group, slug in pack["photo_groups"].items():
            if not files.get(group):
                summary["group missing files"] += 1
                continue
            for lang in ("ar", "en"):
                page = ContentPage.objects.filter(
                    slug=slug, locale__language_code=lang, kind="project"
                ).first()
                if not page:
                    summary["project not found"] += 1
                    continue
                marker = "kfata-2026-photo-v1:" + group + ":" + lang
                if PresentationUpdate.objects.filter(page=page, key=marker).exists():
                    summary["previously attached"] += 1
                    continue
                if locked_by_editor(page):
                    summary["editor draft preserved"] += 1
                    continue
                if not options["apply"]:
                    summary["would attach gallery"] += 1
                    continue
                selected = images[group]
                if not selected:
                    continue
                # Keep existing images and hand-curated galleries; append a new
                # separately named source gallery instead of overwriting it.
                block_title = "صور إضافية من ملف الشركة" if lang == "ar" else "More photographs from the company profile"
                previous = [(b.block_type, b.value) for b in page.body]
                previous.append(("gallery", {
                    "visible": True, "tone": "stone", "title": block_title,
                    "images": [{"image": im, "caption": ""} for im in selected],
                }))
                page.body = previous
                if page.hero_image_id is None:
                    page.hero_image = selected[0]
                revision = page.save_revision()
                if options["publish"] and page.live:
                    revision.publish()
                # Preserve any older draft-only page as draft, including
                # projects withheld for attribution review.
                PresentationUpdate.objects.create(page=page, key=marker)
                summary["galleries attached"] += 1

        for group in pack["review_only_photo_groups"]:
            summary["review-only images (not displayed)"] += len(files.get(group, []))
        prefix = "APPLIED" if options["apply"] else "PREVIEW ONLY — no database changes"
        self.stdout.write(prefix + ": " + ", ".join(
            str(summary[key]) + " " + key for key in sorted(summary)
        ))
