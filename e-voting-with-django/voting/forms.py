from django import forms
from .models import *
from account.forms import FormSettings
from django.contrib.admin import widgets 


class VoterForm(FormSettings):
    # BRANCH = ((1,"Architectural"), (2,"biomedical"), (3,"civil"), (4,"mechanical"), (5,"electrical"), (6,"aerospace"), (7,"CS"), (8,"chemical"))
    # branch = forms.ChoiceField(choices = BRANCH, label="branch", initial='', widget=forms.Select(), required=True)
    class Meta:
        model = Voter
        fields = ['phone', 'branch']

class BranchesForm(FormSettings):
    # BRANCH = ((1,"Architectural"), (2,"biomedical"), (3,"civil"), (4,"mechanical"), (5,"electrical"), (6,"aerospace"), (7,"CS"), (8,"chemical"))
    # branch = forms.ChoiceField(choices = BRANCH, label="branch", initial='', widget=forms.Select(), required=True)
    class Meta:
        model = Branches
        fields = ['bid', 'name']


class PositionForm(FormSettings):
    class Meta:
        model = Position
        fields = ['name', 'max_vote','voter_count','candidate_count','allowed_branches','init_time','init_date','end_time', 'end_date']
        widgets = {
            'init_date': forms.widgets.DateInput(attrs={'type': 'date'}),
            'init_time': forms.widgets.DateInput(attrs={'type': 'time'}),
            'end_date': forms.widgets.DateInput(attrs={'type': 'date'}),
            'end_time': forms.widgets.DateInput(attrs={'type': 'time'})
        }
        

class CandidateForm(FormSettings):
    class Meta:
        model = Candidate
        fields = ['fullname', 'bio', 'position', 'photo']
