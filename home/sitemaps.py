from wagtail.contrib.sitemaps.sitemap_generator import Sitemap


class PublicSitemap(Sitemap):
    def items(self):
        # The structural root redirects to /ar/; list canonical content pages.
        return super().items().filter(depth__gte=2)
