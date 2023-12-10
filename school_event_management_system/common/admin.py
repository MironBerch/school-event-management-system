from os import environ

from django.contrib import admin

admin.site.site_title = f"Админ-панель {environ.get('SCHOOL_NAME')}"
admin.site.site_header = f"Админ-панель {environ.get('SCHOOL_NAME')}"
