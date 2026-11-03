from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock

class Heading(blocks.StructBlock):
    eyebrow = blocks.CharBlock(required=False)
    title = blocks.CharBlock()
    text = blocks.RichTextBlock(required=False, features=['bold', 'italic', 'link', 'ul', 'ol'])
    class Meta:
        template = 'home/blocks/heading.html'
        icon = 'title'
        label = 'عنوان ونص / Heading'

class ImageText(blocks.StructBlock):
    title = blocks.CharBlock()
    text = blocks.RichTextBlock(features=['bold', 'italic', 'link', 'ul', 'ol'])
    image = ImageChooserBlock()
    reverse = blocks.BooleanBlock(required=False)
    class Meta:
        template = 'home/blocks/image_text.html'
        icon = 'image'
        label = 'صورة ونص / Image and text'

class Gallery(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    images = blocks.ListBlock(blocks.StructBlock([
        ('image', ImageChooserBlock()), ('caption', blocks.CharBlock(required=False)),
    ]))
    class Meta:
        template = 'home/blocks/gallery.html'
        icon = 'image'
        label = 'معرض صور / Gallery'

class CallToAction(blocks.StructBlock):
    title = blocks.CharBlock()
    text = blocks.CharBlock(required=False)
    button_label = blocks.CharBlock()
    page = blocks.PageChooserBlock(required=False)
    class Meta:
        template = 'home/blocks/cta.html'
        icon = 'link'

class FAQ(blocks.StructBlock):
    title = blocks.CharBlock()
    items = blocks.ListBlock(blocks.StructBlock([
        ('question', blocks.CharBlock()), ('answer', blocks.TextBlock()),
    ]))
    class Meta:
        template = 'home/blocks/faq.html'
        icon = 'help'

class Listing(blocks.StructBlock):
    title = blocks.CharBlock()
    kind = blocks.ChoiceBlock(choices=[('project', 'المشروعات / Projects'), ('service', 'الخدمات / Services'), ('article', 'الأخبار / News'), ('sector', 'القطاعات / Sectors')])
    count = blocks.IntegerBlock(default=6, min_value=1, max_value=24)
    class Meta:
        template = 'home/blocks/listing.html'
        icon = 'list-ul'

class DocumentLink(blocks.StructBlock):
    label = blocks.CharBlock()
    document = DocumentChooserBlock()
    class Meta:
        template = 'home/blocks/document.html'
        icon = 'doc-full'

class SiteBody(blocks.StreamBlock):
    heading = Heading()
    image_text = ImageText()
    gallery = Gallery()
    listing = Listing()
    faq = FAQ()
    cta = CallToAction()
    document = DocumentLink()
    hero = blocks.StructBlock([
        ('title', blocks.CharBlock()), ('text', blocks.TextBlock(required=False)),
        ('image', ImageChooserBlock(required=False)), ('button_label', blocks.CharBlock(required=False)),
        ('page', blocks.PageChooserBlock(required=False)),
    ], template='home/blocks/hero.html', icon='image')
    statistics = blocks.StructBlock([
        ('title', blocks.CharBlock(required=False)),
        ('items', blocks.ListBlock(blocks.StructBlock([
            ('value', blocks.CharBlock()), ('label', blocks.CharBlock()),
            ('source', blocks.CharBlock(help_text='Approved source and date; kept in the editor.')),
        ]))),
    ], template='home/blocks/statistics.html', icon='list-ul')
    video = blocks.StructBlock([
        ('title', blocks.CharBlock()),
        ('video', DocumentChooserBlock(help_text='Approved MP4/WebM only; no autoplay or external tracking.')),
        ('poster', ImageChooserBlock(required=False)), ('transcript', blocks.TextBlock()),
    ], template='home/blocks/video.html', icon='media')
