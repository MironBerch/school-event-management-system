from random import choice, randint
from typing import Any

from faker import Faker

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from accounts.models import Profile, User
from events.models import Event, EventStageChoices, EventStatusChoices, EventTypeChoices

BASE_DIR = settings.BASE_DIR

faker = Faker('ru_RU')


def create_fake_user(
        email: str,
        name: str,
        surname: str,
        patronymic: str,
        password: str,
) -> User:
    """Create `User` use fake data."""
    user = User.objects.create_user(
        email=email,
        name=name,
        surname=surname,
        patronymic=patronymic,
        password=password,
    )
    return user


def edit_fake_user_profile(user: User) -> None:
    """Edit fake user's `Profile` use fake data."""
    profile = Profile.objects.get(user=user)
    profile.year_of_study = faker.random_int(min=1, max=11)
    profile.save()


def create_fake_users_and_edit_profiles(coefficient: float = 1) -> None:
    """Create users and edit their profiles use fake data."""
    for _ in range(int(100 * coefficient)):
        edit_fake_user_profile(
            user=create_fake_user(
                email=faker.unique.email(),
                name=faker.first_name(),
                surname=faker.last_name(),
                patronymic=faker.first_name_male(),
                password=faker.password(length=10),
            ),
        )


def create_fake_events(coefficient: float = 1) -> None:
    """Create events use fake data."""
    used_names = set()
    for _ in range(int(20 * coefficient)):
        while True:
            name = f'Мероприятие {Event.objects.count() + 1}'
            if name not in used_names:
                used_names.add(name)
                break
        maximum_number_of_team_members = randint(2, 8)
        event = Event.objects.create(
            name=name,
            slug=slugify(name),
            description=faker.paragraph(),
            maximum_number_of_team_members=maximum_number_of_team_members,
            minimum_number_of_team_members=randint(1, maximum_number_of_team_members),
            status=choice(EventStatusChoices.values),
            type=choice(EventTypeChoices.values),
            stage=choice(EventStageChoices.values),
            date_of_starting_registration=faker.future_date(),
            date_of_ending_registration=faker.future_date(),
            date_of_starting_event=faker.future_date(),
            published=faker.pybool(),
        )
        event.save()


class Command(BaseCommand):
    """
    Command for create fake content. Fills the database with fake data.\n

    `coefficient` - coefficient by which the amount of fake data
    is determined which uploaded in database (default value is 1).\n

    Formula:\n
    100 users * `coefficient` \n
    20 events * `coefficient`
    """

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            'coefficient',
            type=float,
            help='Indicates the coefficient of fakedata',
        )

    def handle(self, *args: Any, **kwargs: Any) -> None:
        coefficient = kwargs['coefficient']

        Faker.seed(0)

        create_fake_users_and_edit_profiles(coefficient=coefficient)
        create_fake_events(coefficient=coefficient)
