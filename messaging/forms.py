from django import forms
from .models import DirectMessage, CommunityMessage

class DirectMessageForm(forms.ModelForm):
    class Meta:
        model = DirectMessage
        fields = ['content', 'file']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Type your message here...'}),
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content and not self.cleaned_data.get('file'):
            raise forms.ValidationError("You must provide either a message or a file.")
        return content

class CommunityMessageForm(forms.ModelForm):
    class Meta:
        model = CommunityMessage
        fields = ['content', 'file']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Share with the community...'}),
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content and not self.cleaned_data.get('file'):
            raise forms.ValidationError("You must provide either a message or a file.")
        return content

class UserSearchForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search for a user...'})
    )
