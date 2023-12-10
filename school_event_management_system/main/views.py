from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class SitemapView(
    LoginRequiredMixin,
    TemplateView,
):
    """View for display site map."""

    template_name = 'main/site_map.html'
