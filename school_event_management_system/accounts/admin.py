from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.safestring import mark_safe

from accounts.forms import AdminUserChangeForm, SignUpForm
from accounts.models import Profile, User

admin.site.unregister(Group)


class ProfileInline(admin.StackedInline):
    model = Profile


@admin.register(User)
class UserAdmin(UserAdmin):
    inlines = [ProfileInline]
    list_display = (
        'email',
        'surname',
        'name',
        'patronymic',
        'get_profile_admin_link',
    )
    search_fields = (
        'email',
        'name',
        'surname',
    )
    readonly_fields = (
        'id',
        'date_joined',
        'last_login',
    )
    ordering = ('surname', )
    list_filter = (
        'is_active',
        'is_staff',
        'is_superuser',
        'is_email_confirmed',
        'role',
    )

    form = AdminUserChangeForm
    fieldsets = (
        (
            None,
            {
                'fields': ('email',),
            },
        ),
        (
            'Личная информация', {
                'fields': (
                    'surname',
                    'name',
                    'patronymic',
                ),
            },
        ),
        (
            'Разрешения', {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'is_email_confirmed',
                    'role',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
        (
            'Важные даты',
            {
                'fields': (
                    'last_login',
                    'date_joined',
                ),
            },
        ),
    )

    add_form = SignUpForm
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide', ),
                'fields': (
                    'email',
                    'name',
                    'surname',
                    'patronymic',
                    'role',
                    'password1',
                    'password2',
                ),
            },
        ),
    )

    def get_profile_admin_link(self, obj: User):
        return mark_safe(
            f"""<a href="{
                reverse('admin:accounts_profile_change', args=(obj.id, ))
            }">Просмотреть</a>""",
        )

    get_profile_admin_link.short_description = 'Ссылка на профиль в панели администратора'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'date_of_birth',
        'year_of_study',
        'school',
        'phone_number',
        'get_user_admin_link',
    )
    search_fields = (
        'user__email',
        'user__name',
        'user__surname',
    )
    list_filter = ('year_of_study', )

    def get_user_admin_link(self, obj: User):
        return mark_safe(
            f"""<a href="{
                reverse('admin:accounts_user_change', args=(obj.id, ))
            }">Просмотреть</a>""",
        )

    get_user_admin_link.short_description = 'Ссылка на пользователя в панели администратора'
