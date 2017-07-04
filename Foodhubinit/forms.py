from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class SignUpForm(UserCreationForm):
	first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
	last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
	email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

	def __init__(self, *args, **kwargs):
		super(SignUpForm, self).__init__(*args, **kwargs)
		self.fields['password1'].help_text = "Your password can't be too similar to your other personal information.Your password must contain at least 8 characters"

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name','email', 'password1', 'password2', )

# class BootstrapPaginator(Paginator):
#     def __init__(self, *args, **kwargs):
#         """        
#         :param wing_pages: How many pages will be shown before and after current page.
#         """
#         self.wing_pages = kwargs.pop('wing_pages', 3)
#         super(BootstrapPaginator, self).__init__(*args, **kwargs)

#     def _get_page(self, *args, **kwargs):
#         self.page = super(BootstrapPaginator, self)._get_page(*args, **kwargs)
#         return self.page

#     @property
#     def page_range(self):
#         return range(max(self.page.number - self.wing_pages, 1),
#                      min(self.page.number + self.wing_pages + 1, self.num_pages + 1))

class UpdateUserName(forms.ModelForm):
	first_name = forms.CharField(required=True)
	last_name = forms.CharField(required=True)
	username = forms.CharField(required=False)
	email = forms.EmailField(required=False)

	class Meta:
		model = User
		fields = ('username', 'email', 'first_name', 'last_name')

	def save(self, commit=True):
		user = super(RegistrationForm, self).save(commit=False)
		user.email = self.cleaned_data['email']

		if commit:
			user.save()

		return user

class EditNameForm(forms.ModelForm):

    first_name = forms.CharField(help_text='Required. Inform a valid email address.',widget=forms.TextInput(attrs={'required':True,'class': 'f-form-field f-form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'required':True,'class': 'f-form-field f-form-control'})) 

    class Meta:
        model = User
        fields = ('first_name', 'last_name')

    def save(self, *args, **kwargs):
      """
      Update the primary email address on the related User object as well. 
      """
      u = self.instance.user
      u.first_name = self.cleaned_data['first_name']
      u.last_name = self.cleaned_data['last_name']
      u.save()
      profile = super(EditProfileForm, self).save(*args,**kwargs)
      return profile

class EditEmailForm(forms.ModelForm):

    email = forms.EmailField(label='New Email', max_length=254,widget=forms.TextInput(attrs={'required':True,'class': 'f-form-field f-form-control'}))
    confirm_email  = forms.EmailField(label='Confirm Email', max_length=254,widget=forms.TextInput(attrs={'required':True,'class': 'f-form-field f-form-control'}))

    class Meta:
        model = User
        fields = ('email',)

    def clean(self):
        cleaned_data = super(EditEmailForm, self).clean()
        email = cleaned_data.get("email")
        confirm_email = cleaned_data.get("confirm_email")

        if email and confirm_email:
        # Only do something if both fields are valid so far.
            if email != confirm_email:
                raise forms.ValidationError("Emails do not match.")

        return cleaned_data    

    def save(self, *args, **kwargs):
      """
      Update the primary email address on the related User object as well. 
      """
      u = self.instance.user
      u.email = self.cleaned_data['email']
      u.save()
      profile = super(EditEmailForm, self).save(*args,**kwargs)
      return profile      