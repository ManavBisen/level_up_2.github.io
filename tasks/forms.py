from django import forms
from django.contrib.auth.models import User
from .models import ExtraTask

class ExtraTaskForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        help_text="Leave empty to assign to all users"
    )
    
    class Meta:
        model = ExtraTask
        fields = ['title', 'description', 'xp_reward', 'assigned_to']


class GoodWorkSessionForm(forms.Form):
    minutes = forms.IntegerField(min_value=1, max_value=120, required=True)
