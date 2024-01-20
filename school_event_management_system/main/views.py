from django.views.generic import TemplateView


class SitemapView(TemplateView):
    """Просмотр для отображения карты сайта."""

    template_name = 'main/site_map.html'


class BadRequestView(TemplateView):
    template_name = 'errors/400.html'
    status_code = 400


class PermissionDeniedView(TemplateView):
    template_name = 'errors/403.html'
    status_code = 403


class PageNotFoundView(TemplateView):
    template_name = 'errors/404.html'
    status_code = 404


class ServerErrorView(TemplateView):
    template_name = 'errors/500.html'
    status_code = 500
