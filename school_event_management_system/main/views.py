from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class SitemapView(
    LoginRequiredMixin,
    TemplateView,
):
    """Просмотр для отображения карты сайта."""

    template_name = 'main/site_map.html'
