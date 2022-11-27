from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Stegno

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class StegForm(forms.ModelForm):
    class Meta:
        model = Stegno
        fields = ["hidden_message","filename", "key"]
        
class StegDecodeForm(forms.ModelForm):
    class Meta:
        model = Stegno
        fields = ["filename", "key"]