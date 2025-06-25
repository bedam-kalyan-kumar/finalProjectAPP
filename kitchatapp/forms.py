from django import forms
from django.contrib.auth.models import User
from .models import Post,Story

# User Registration Form
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

# Post Form (For Image/Video Upload)
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['image', 'video', 'caption']
        widgets = {
            'caption': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write a caption...'}),
        }
        
from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'file']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'message-input',
                'placeholder': 'Type your message...',
                'rows': 3
            }),
            'file': forms.FileInput(attrs={
                'class': 'file-input',
                'accept': 'image/*, video/*'
            })
        }

from django.contrib.auth.forms import AuthenticationForm

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    
class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['content']  # Removed 'text_content'
    
    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        
        if not content:
            raise forms.ValidationError("You must provide media content.")
        
        return cleaned_data

    
    
# forms.py
