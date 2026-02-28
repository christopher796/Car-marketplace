from django import forms
from django.contrib.auth.forms import User
from .models import Profile, Review

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_pic', 'id_front', 'id_back', 'location']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']

class VerificationForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'profile_pic', 'id_front', 'id_back', 'location']
        widgets = {
            'location': forms.TextInput(attrs={'placeholder': 'Enter your location'}),
        }