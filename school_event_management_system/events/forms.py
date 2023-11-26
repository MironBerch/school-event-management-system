from django import forms


class TeamForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        label='Название команды*',
    )


class ParticipantForm(forms.Form):
    def __init__(
            self,
            user,
            *args,
            **kwargs,
    ):
        super(ParticipantForm, self).__init__(*args, **kwargs)
        self.fields['fio'] = forms.CharField(
            max_length=255,
            label='ФИО участника*',
            disabled=True,
            initial=user.full_name,
        )


class SupervisorForm(forms.Form):
    fio = forms.CharField(
        max_length=255,
        label='ФИО руководителя*',
    )


class TeamParticipantsForm(forms.Form):
    def __init__(
            self,
            minimum_number_of_team_members: int,
            maximum_number_of_team_members: int,
            user,
            *args,
            **kwargs,
    ):
        super(TeamParticipantsForm, self).__init__(*args, **kwargs)
        self.fields['participant_1'] = forms.CharField(
            max_length=255,
            label='ФИО 1-го участника*',
            disabled=True,
            initial=user.full_name,
        )
        for i in range(2, maximum_number_of_team_members + 1):
            required = i <= minimum_number_of_team_members
            self.fields[f'participant_{i}'] = forms.CharField(
                max_length=255,
                label=f'ФИО {i}-го участника' + ('*' if required else ''),
                required=required,
            )
