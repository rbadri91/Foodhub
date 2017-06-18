from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    
    def __init__(self, *args, **kwargs):
    	super(SignUpForm, self).__init__(*args, **kwargs)
    	self.fields['password1'].help_text = "Your password can't be too similar to your other personal information.Your password must contain at least 8 characters"
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )