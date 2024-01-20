import debug_toolbar

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from main.views import BadRequestView, PageNotFoundView, PermissionDeniedView, ServerErrorView

handler400 = BadRequestView.as_view()
handler403 = PermissionDeniedView.as_view()
handler404 = PageNotFoundView.as_view()
handler500 = ServerErrorView.as_view()

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('accounts.urls')),
    path('', include('events.urls')),
    path('', include('main.urls')),
    path('', include('mailings.urls')),

    path('', RedirectView.as_view(url='/events/', permanent=True)),

    path('ckeditor/', include('ckeditor_uploader.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
