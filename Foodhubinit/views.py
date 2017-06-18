from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode,  urlsafe_base64_decode
from django.template.loader import render_to_string

from Foodhubinit.forms import SignUpForm
from Foodhubinit.tokens import account_activation_token
import json


# Create your views here.

def index(request):
	json_data = open('Foodhubinit/static/Foodhub/json/us_state_capitals.json')
	data1 = json.load(json_data)
	capitals =list()
	
	for attribute, value in data1.items():
		capitals.append(value['capital'])
	print("capitals:",capitals)	
	return render(request, 'Foodhubinit/index.html',{"capitals":capitals})

@login_required
def home(request):
    return render(request, 'Foodhubinit/home.html')    

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()


            current_site = get_current_site(request)
            subject = 'Activate Your MySite Account'
            message = render_to_string('Foodhubinit/account_activation_email.html', {
                'user': user,
                # 'password': learningapp1,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)

            return redirect('account_activation_sent')
    else:
        form = SignUpForm()
    return render(request, 'Foodhubinit/signup.html', {'form': form})

def account_activation_sent(request):
    return render(request, 'Foodhubinit/account_activation_sent.html')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('home')
    else:
        return render(request, 'Foodhubinit/account_activation_invalid.html')

def listStates(request):
	json_data = open('Foodhubinit/static/Foodhub/json/states_hash.json')
	data1 = json.load(json_data)
	states =list()
	for value in data1.values():
		states.append(value)
	return render(request, 'Foodhubinit/listAllStates.html',{"states":states})

def cities(request,state):
	pass

def custom_login(request):
    if request.user.is_authenticated():
        return redirect('home')
    else:
        return login(request)	