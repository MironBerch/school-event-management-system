from django.urls import path

from main.views import SitemapView

urlpatterns = [
    path(
        route='sitemap/',
        view=SitemapView.as_view(),
        name='site_map',
    ),
]
