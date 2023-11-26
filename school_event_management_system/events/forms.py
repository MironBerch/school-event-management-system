from django import forms

from events.models import Team


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ('name', )

    def __init__(self, *args, **kwargs):
        super(TeamForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Название команды'


class ParticipantRegisterForm(forms.Form):
    fio = forms.CharField(max_length=255)

    def __init__(self, *args, **kwargs):
        super(ParticipantRegisterForm, self).__init__(*args, **kwargs)
        self.fields['fio'].label = 'ФИО участника'
