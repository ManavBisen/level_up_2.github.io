from django import forms
from .models import DirectMessage, CommunityMessage

class DirectMessageForm(forms.ModelForm):
    class Meta:
        model = DirectMessage
        fields = ['content', 'file', 'audio']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Type your message here...'}),
            'audio': forms.HiddenInput(),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        file = cleaned_data.get('file')
        audio = cleaned_data.get('audio')
        
        # Ensure at least one of content, file or audio is provided
        if not content and not file and not audio:
            raise forms.ValidationError("You must provide a message, a file, or record an audio message.")
        
        return cleaned_data

class CommunityMessageForm(forms.ModelForm):
    class Meta:
        model = CommunityMessage
        fields = ['content', 'file', 'audio']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Share with the community...'}),
            'audio': forms.HiddenInput(),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        file = cleaned_data.get('file')
        audio = cleaned_data.get('audio')
        
        # Ensure at least one of content, file or audio is provided
        if not content and not file and not audio:
            raise forms.ValidationError("You must provide a message, a file, or record an audio message.")
        
        return cleaned_data

class UserSearchForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search for a user...'})
    )
