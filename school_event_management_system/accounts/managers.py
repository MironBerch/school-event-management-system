from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Менеджер пользовательской модели `User`."""

    use_in_migrations = True

    def create_user(
            self,
            email: str,
            name: str,
            surname: str,
            password: str = None,
            **extra_fields,
    ):
        if not email:
            return ValueError('Пользователи должны иметь адрес электронной почты.')
        if not name:
            return ValueError('У пользователей должно быть имя.')
        if not surname:
            return ValueError('Пользователи должны иметь фамилию.')
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            surname=surname,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(
            self,
            email: str,
            name: str,
            surname: str,
            password: str,
            **extra_fields,
    ):
        user = self.create_user(
            email=email,
            name=name,
            surname=surname,
            password=password,
            **extra_fields,
        )
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_superuser(
            self,
            email: str,
            name: str,
            surname: str,
            password: str,
            **extra_fields,
    ):
        user = self.create_user(
            email=email,
            name=name,
            surname=surname,
            password=password,
            **extra_fields,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class ActivatedAccountsManager(UserManager):
    """Менеджер для всех пользователей, подтвердивших свой адрес электронной почты."""

    def get_queryset(self):
        base_queryset = super(ActivatedAccountsManager, self).get_queryset()
        return base_queryset.filter(is_email_confirmed=True)
