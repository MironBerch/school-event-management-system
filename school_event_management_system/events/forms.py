from django import forms

from accounts.services import get_user_by_fio
from events.models import Solution
from events.services import team_with_name_exist_in_event


class TeamForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        label='Название команды*',
    )
    school_class = forms.CharField(
        max_length=5,
        label='Класс который представляет команда*',
    )

    def __init__(self, team=None, event=None, event_for_classes: bool = False, *args, **kwargs):
        self.event = event
        self.team = team
        super(TeamForm, self).__init__(*args, **kwargs)
        if not event_for_classes:
            self.fields['school_class'].widget = forms.HiddenInput()
            self.fields['school_class'].required = False

    def clean_name(self):
        team_name = str(self.cleaned_data['name'])
        if self.team and self.team.name:
            if team_name != self.team.name and team_with_name_exist_in_event(
                event=self.event,
                team_name=team_name,
            ):
                raise forms.ValidationError(
                    'Команда с таким названием уже участвует в мероприятии',
                )
        else:
            if team_with_name_exist_in_event(event=self.event, team_name=team_name):
                raise forms.ValidationError(
                    'Команда с таким названием уже участвует в мероприятии',
                )
        return team_name


class ParticipantForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(ParticipantForm, self).__init__(*args, **kwargs)
        if user.role == 'ученик':
            self.fields['participant_fio'] = forms.CharField(
                max_length=255,
                label='ФИО участника*',
                disabled=True,
                initial=user.full_name,
            )
        else:
            self.fields['participant_fio'] = forms.CharField(
                max_length=255,
                label='ФИО участника*',
                initial=None,
            )

    def clean(self):
        cleaned_data = super().clean()
        fio = cleaned_data.get('participant_fio')
        user = get_user_by_fio(fio)
        if not user:
            raise forms.ValidationError('Нет пользователя с таким ФИО')
        if user.role != 'ученик':
            raise forms.ValidationError('Пользователь должен являться учеником')
        return cleaned_data


class SupervisorForm(forms.Form):
    fio = forms.CharField(
        max_length=255,
        label='ФИО руководителя*',
    )

    def clean_fio(self):
        fio = self.cleaned_data.get('fio')
        user = get_user_by_fio(fio)
        if not user:
            raise forms.ValidationError('Нет пользователя с таким ФИО')
        else:
            if user.role == 'ученик':
                raise forms.ValidationError('Пользователь не должен являться учеником')
        return fio


class TeamParticipantsForm(forms.Form):
    def __init__(
            self,
            minimum_number_of_team_members: int,
            maximum_number_of_team_members: int,
            *args,
            **kwargs,
    ):
        super(TeamParticipantsForm, self).__init__(*args, **kwargs)
        self.maximum_number_of_team_members = maximum_number_of_team_members
        for i in range(1, maximum_number_of_team_members + 1):
            required = i <= minimum_number_of_team_members
            self.fields[f'participant_{i}'] = forms.CharField(
                max_length=255,
                label=f'ФИО {i}-го участника' + ('*' if required else ''),
                required=required,
            )

    def clean(self):
        cleaned_data = super().clean()
        for i in range(1, self.maximum_number_of_team_members + 1):
            field_name = f'participant_{i}'
            fio = cleaned_data.get(field_name)
            if fio:
                user = get_user_by_fio(fio)
                if not user:
                    self.add_error(field_name, 'Нет пользователя с таким ФИО')
                else:
                    if user.role != 'ученик':
                        self.add_error(field_name, 'Пользователь должен являться учеником')
        return cleaned_data


class SolutionForm(forms.ModelForm):
    class Meta:
        model = Solution
        fields = ('url', )


class TeamOrParticipantForm(forms.Form):
    team_id = forms.ChoiceField(choices=[], label='Команда')
    participant_id = forms.ChoiceField(choices=[], label='Участник')

    def __init__(self, *args, participants=None, teams=None, **kwargs):
        super().__init__(*args, **kwargs)
        if teams is not None:
            choices = [(object.id, str(object.name)) for object in teams]
            self.fields['team_id'].choices = choices
            self.fields['participant_id'].widget = forms.HiddenInput()
            self.fields['participant_id'].required = False
        if participants is not None:
            choices = [(object.id, str(object.user.full_name)) for object in participants]
            self.fields['participant_id'].choices = choices
            self.fields['team_id'].widget = forms.HiddenInput()
            self.fields['team_id'].required = False
