from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    
    def __init__(self, *args, **kwargs):
    	super(SignUpForm, self).__init__(*args, **kwargs)
    	self.fields['password1'].help_text = "Your password can't be too similar to your other personal information.Your password must contain at least 8 characters"
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )

class BootstrapPaginator(Paginator):
    def __init__(self, *args, **kwargs):
        """        
        :param wing_pages: How many pages will be shown before and after current page.
        """
        self.wing_pages = kwargs.pop('wing_pages', 3)
        super(BootstrapPaginator, self).__init__(*args, **kwargs)

    def _get_page(self, *args, **kwargs):
        self.page = super(BootstrapPaginator, self)._get_page(*args, **kwargs)
        return self.page

    @property
    def page_range(self):
        return range(max(self.page.number - self.wing_pages, 1),
                     min(self.page.number + self.wing_pages + 1, self.num_pages + 1))