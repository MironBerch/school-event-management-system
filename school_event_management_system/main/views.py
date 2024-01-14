from django.views.generic import TemplateView


class SitemapView(TemplateView):
    """Просмотр для отображения карты сайта."""

    template_name = 'main/site_map.html'
