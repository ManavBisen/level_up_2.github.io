from django import forms
from django.contrib.auth.models import User
from .models import ExtraTask

class ExtraTaskForm(forms.ModelForm):
    target_username = forms.CharField(max_length=150, required=False, help_text="Leave blank for a global task")
    
    class Meta:
        model = ExtraTask
        fields = ['name', 'description', 'xp_reward', 'is_global', 'stock', 'expires_at']
        widgets = {
            'expires_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['expires_at'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        target_username = cleaned_data.get('target_username')
        is_global = cleaned_data.get('is_global')
        
        if not is_global and not target_username:
            raise forms.ValidationError("You must either specify a target username or mark the task as global.")
        
        if is_global and target_username:
            raise forms.ValidationError("A task cannot be both global and targeted to a specific user.")
        
        if target_username:
            try:
                user = User.objects.get(username=target_username)
                cleaned_data['target_user'] = user
            except User.DoesNotExist:
                raise forms.ValidationError(f"User '{target_username}' does not exist.")
        
        return cleaned_data
