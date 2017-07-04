from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode,  urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.contrib import messages
import json
from bson import json_util
from bson.json_util import dumps
import urllib
import urllib.request,urllib.parse
import requests
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import collections
import operator
from django.contrib.auth import views

from Foodhubinit.forms import SignUpForm, EditNameForm, EditEmailForm
from Foodhubinit.tokens import account_activation_token
import json
from decimal import *
from functools import wraps


# Create your views here.

class persist_session_vars(object):
    """
    Some views, such as login and logout, will reset all session state.
    (via a call to ``request.session.cycle_key()`` or ``session.flush()``).
    That is a security measure to mitigate session fixation vulnerabilities.

    By applying this decorator, some values are retained.
    Be very aware what find of variables you want to persist.
    """

    def __init__(self, vars):
        self.vars = vars

    def __call__(self, view_func):

        @wraps(view_func)
        def inner(request, *args, **kwargs):
            # Backup first
            session_backup = {}
            for var in self.vars:
                try:
                	print("session var saved here:",var)
                	session_backup[var] = request.session[var]
                except KeyError:
                    pass

            # Call the original view
            response = view_func(request, *args, **kwargs)

            # Restore variables in the new session
            for var, value in session_backup.items():
            	print("variables restored:",var);
            	request.session[var] = value

            return response

        return inner

def index(request):
	json_data = open('Foodhubinit/static/Foodhub/json/us_state_capitals.json')
	data1 = json.load(json_data)
	capitals =list()
	request.session['cities'] = {}
	request.session.modified = True

	isLoggedIn =False
	username =""
	if request.user.is_authenticated():
		isLoggedIn = True
		username = request.user.username

	productsChosen = list();
	sectionList = list();
	itemNamesList = list();

	print("in index function")
	order_type = "delivery"

	if "order_type" in request.session:
		order_type = request.session["order_type"]

	if order_type == "delivery":
		order_type ="Delivery"
	else:
		order_type ="Pick Up"

	address =""
	productDetails=[]
	if "order_address" in request.session:
		address = request.session["order_address"]

	restaurantName =""
	if "restaurantName" in request.session:
		restaurantName = request.session["restaurantName"]	

	if "productsChosen" in request.session:
		productsChosen = request.session["productsChosen"]

	if "sectionNames" in request.session:
		sectionList = request.session["sectionNames"]

	if "itemNameList" in request.session:
		itemNamesList = request.session["itemNameList"]

	totalPrice =0

	if "subTotal" in request.session:
		totalPrice = request.session["subTotal"] 

	totalAmount =0

	if 'totalAmt' in request.session:
		totalAmount = request.session["totalAmt"]

	deliveryMin =0.0
	if 'deliveryMin' in request.session:
		deliveryMin = request.session["deliveryMin"]

	deliveryPrice =0.0
	if 'deliveryPrice' in request.session:
		deliveryPrice = request.session["deliveryPrice"]	

	salesTax =0.0
	if 'salestax' in request.session:
		salesTax = request.session["salestax"]	

	productDetails =[]
	if len(productsChosen) !=0:
		productDetails = zip(productsChosen, sectionList, itemNamesList)	

				
	request.session["isMenuPage"] =False
	
	for attribute, value in data1.items():
		capitals.append(value['capital'])
	return render(request, 'Foodhubinit/index.html',
		{"capitals":capitals,
		"order_type":order_type,
		"dest_address":address,
		"restaurantName":restaurantName,
		"productsChosen":productDetails,
		"subTotal":totalPrice,
		"totalAmt":totalAmount,
		"deliveryMin":deliveryMin,
		"deliveryPrice":deliveryPrice,
		"salesTax":salesTax,
		"isLoggedIn":isLoggedIn,
		"username":username
		})

@login_required
def home(request):
	json_data = open('Foodhubinit/static/Foodhub/json/us_state_capitals.json')
	data1 = json.load(json_data)
	capitals =list()
	request.session['cities'] = {}
	request.session.modified = True

	isLoggedIn =False
	username = request.user.username

	productsChosen = list();
	sectionList = list();
	itemNamesList = list();

	print("in index function")
	order_type = "delivery"

	if "order_type" in request.session:
		order_type = request.session["order_type"]

	if order_type == "delivery":
		order_type ="Delivery"
	else:
		order_type ="Pick Up"

	address =""
	productDetails=[]
	if "order_address" in request.session:
		address = request.session["order_address"]

	restaurantName =""
	if "restaurantName" in request.session:
		restaurantName = request.session["restaurantName"]	

	if "productsChosen" in request.session:
		productsChosen = request.session["productsChosen"]

	if "sectionNames" in request.session:
		sectionList = request.session["sectionNames"]

	if "itemNameList" in request.session:
		itemNamesList = request.session["itemNameList"]

	totalPrice =0

	if "subTotal" in request.session:
		totalPrice = request.session["subTotal"] 

	totalAmount =0

	if 'totalAmt' in request.session:
		totalAmount = request.session["totalAmt"]

	deliveryMin =0.0
	if 'deliveryMin' in request.session:
		deliveryMin = request.session["deliveryMin"]

	deliveryPrice =0.0
	if 'deliveryPrice' in request.session:
		deliveryPrice = request.session["deliveryPrice"]	

	salesTax =0.0
	if 'salestax' in request.session:
		salesTax = request.session["salestax"]	

	productDetails =[]
	if len(productsChosen) !=0:
		productDetails = zip(productsChosen, sectionList, itemNamesList)	

				
	request.session["isMenuPage"] =False
	
	for attribute, value in data1.items():
		capitals.append(value['capital'])
	return render(request, 'Foodhubinit/home.html',
		{"capitals":capitals,
		"order_type":order_type,
		"dest_address":address,
		"restaurantName":restaurantName,
		"productsChosen":productDetails,
		"subTotal":totalPrice,
		"totalAmt":totalAmount,
		"deliveryMin":deliveryMin,
		"deliveryPrice":deliveryPrice,
		"salesTax":salesTax,
		"username":username
		})   

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.first_name = first_name
            user.last_name = last_name
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

	productsChosen = list();
	sectionList = list();
	itemNamesList = list();

	isLoggedIn =False
	username =""
	if request.user.is_authenticated():
		isLoggedIn = True
		username = request.user.username

	order_type = "delivery"

	if "order_type" in request.session:
		order_type = request.session["order_type"]
	if order_type == "delivery":
		order_type ="Delivery"
	else:
		order_type ="Pick Up"

	address =""
	productDetails=[]
	if "order_address" in request.session:
		address = request.session["order_address"]

	restaurantName =""
	if "restaurantName" in request.session:
		restaurantName = request.session["restaurantName"]	

	if "productsChosen" in request.session:
		productsChosen = request.session["productsChosen"]

	if "sectionNames" in request.session:
		sectionList = request.session["sectionNames"]

	if "itemNameList" in request.session:
		itemNamesList = request.session["itemNameList"]

	totalPrice =0

	if "subTotal" in request.session:
		totalPrice = request.session["subTotal"] 

	totalAmount =0

	if 'totalAmt' in request.session:
		totalAmount = request.session["totalAmt"]

	deliveryMin =0.0
	if 'deliveryMin' in request.session:
		deliveryMin = request.session["deliveryMin"]

	deliveryPrice =0.0
	if 'deliveryPrice' in request.session:
		deliveryPrice = request.session["deliveryPrice"]	

	salesTax =0.0
	if 'salestax' in request.session:
		salesTax = request.session["salestax"]	

	productDetails =[]
	if len(productsChosen) !=0:
		productDetails = zip(productsChosen, sectionList, itemNamesList)	


	for value in data1.values():
		states.append(value)
	return render(request, 'Foodhubinit/listAllStates.html',
		{"states":states,
		"order_type":order_type,
		"dest_address":address,
		"restaurantName":restaurantName,
		"productsChosen":productDetails,
		"subTotal":totalPrice,
		"totalAmt":totalAmount,
		"deliveryMin":deliveryMin,
		"deliveryPrice":deliveryPrice,
		"salesTax":salesTax,
		"isLoggedIn":isLoggedIn,
		"username":username})

def cities(request,state_name):
	json_data = open('Foodhubinit/static/Foodhub/json/cities.json')
	data = json.load(json_data)
	cities = list();

	productsChosen = list();
	sectionList = list();
	itemNamesList = list();

	isLoggedIn =False
	username =""
	if request.user.is_authenticated():
		isLoggedIn = True
		username = request.user.username

	order_type = "delivery"

	if "order_type" in request.session:
		order_type = request.session["order_type"]
	if order_type == "delivery":
		order_type ="Delivery"
	else:
		order_type ="Pick Up"

	address =""
	productDetails=[]
	if "order_address" in request.session:
		address = request.session["order_address"]

	restaurantName =""
	if "restaurantName" in request.session:
		restaurantName = request.session["restaurantName"]	

	if "productsChosen" in request.session:
		productsChosen = request.session["productsChosen"]

	if "sectionNames" in request.session:
		sectionList = request.session["sectionNames"]

	if "itemNameList" in request.session:
		itemNamesList = request.session["itemNameList"]

	totalPrice =0

	if "subTotal" in request.session:
		totalPrice = request.session["subTotal"] 

	totalAmount =0

	if 'totalAmt' in request.session:
		totalAmount = request.session["totalAmt"]

	deliveryMin =0.0
	if 'deliveryMin' in request.session:
		deliveryMin = request.session["deliveryMin"]

	deliveryPrice =0.0
	if 'deliveryPrice' in request.session:
		deliveryPrice = request.session["deliveryPrice"]	

	salesTax =0.0
	if 'salestax' in request.session:
		salesTax = request.session["salestax"]	

	productDetails =[]
	if len(productsChosen) !=0:
		productDetails = zip(productsChosen, sectionList, itemNamesList)	


	for cityObj in data:
		if cityObj['state'] == state_name:
			cities.append(cityObj['city'])

	print("citiesNew:",cities)
	# json_data = open('Foodhubinit/static/Foodhub/json/counties.json')
	# data1 = json.load(json_data)
	# cities = data1.get(state_name)
	request.session["cities"] = cities
	return render(request, 'Foodhubinit/listAllCities.html',
		{"cities":cities,
		"order_type":order_type,
		"dest_address":address,
		"restaurantName":restaurantName,
		"productsChosen":productDetails,
		"subTotal":totalPrice,
		"totalAmt":totalAmount,
		"deliveryMin":deliveryMin,
		"deliveryPrice":deliveryPrice,
		"salesTax":salesTax,
		"isLoggedIn":isLoggedIn,
		"username":username})

def city(request,city_name):
	json_data = open('Foodhubinit/static/Foodhub/json/cities.json')
	data1 = json.load(json_data)
	nearbyCities = list()
	ratings =dict();
	print("city_name:",city_name)
	state = ""
	if request.session["cities"]:
		nearbyCities = request.session["cities"]
	else:
		for cityObj in data1:
			if cityObj['city'] == city_name:
				state = cityObj['state']
				break

		for cityObj2 in data1:
			if cityObj2['state'] == state:
					nearbyCities.append(cityObj2['city'])

	nearbyCities= sorted(nearbyCities,key=str.lower);
	pageNum = request.GET.get('pageNum')
	if city_name in nearbyCities:
		nearbyCities.remove(city_name)
	# if(not("city" in request.session) or (pageNum == 1 and request.session["city"] != city_name)):
	
	restaurants = getRestaurants("delivery",city_name)
	request.session["restaurants"] = restaurants;
	# else:
		# restaurants = request.session["restaurants"]
	request.session["city"] = city_name	
	totalRestaurants = len(restaurants)
	paginator = Paginator(restaurants, 20)
	try:
		displayRestaurants = paginator.page(pageNum)
	except PageNotAnInteger:
		displayRestaurants = paginator.page(1)
	except EmptyPage:
		displayRestaurants = paginator.page(paginator.num_pages)
	# displayRestaurants = restaurants[(pageNum-1)* 20 : ((pageNum-1)* 20 +20 )]
	index = displayRestaurants.number - 1 
	max_index = len(paginator.page_range)
	start_index = index - 2 if index >= 2 else 0
	end_index = index + 2 if index <= max_index - 2 else max_index
	page_range = paginator.page_range[start_index:end_index]
	request.session["isMenuPage"] =False

	productsChosen = list();
	sectionList = list();
	itemNamesList = list();

	isLoggedIn =False
	username =""
	if request.user.is_authenticated():
		isLoggedIn = True
		username = request.user.username

	order_type = "delivery"

	if "order_type" in request.session:
		order_type = request.session["order_type"]
	if order_type == "delivery":
		order_type ="Delivery"
	else:
		order_type ="Pick Up"

	address =""
	productDetails=[]
	if "order_address" in request.session:
		address = request.session["order_address"]

	restaurantName =""
	if "restaurantName" in request.session:
		restaurantName = request.session["restaurantName"]	

	if "productsChosen" in request.session:
		productsChosen = request.session["productsChosen"]

	if "sectionNames" in request.session:
		sectionList = request.session["sectionNames"]

	if "itemNameList" in request.session:
		itemNamesList = request.session["itemNameList"]

	totalPrice =0

	if "subTotal" in request.session:
		totalPrice = request.session["subTotal"] 

	totalAmount =0

	if 'totalAmt' in request.session:
		totalAmount = request.session["totalAmt"]

	deliveryMin =0.0
	if 'deliveryMin' in request.session:
		deliveryMin = request.session["deliveryMin"]

	deliveryPrice =0.0
	if 'deliveryPrice' in request.session:
		deliveryPrice = request.session["deliveryPrice"]	

	salesTax =0.0
	if 'salestax' in request.session:
		salesTax = request.session["salestax"]	

	productDetails =[]
	if len(productsChosen) !=0:
		productDetails = zip(productsChosen, sectionList, itemNamesList)	



	return render(request, 'Foodhubinit/listCityRestaurants.html',
		{"city":city_name,
		"nearby_cities":nearbyCities,
		"restaurants":displayRestaurants,
		"total":totalRestaurants,
		"ratings":ratings,
		"page_range":page_range,
		"order_type":order_type,
		"dest_address":address,
		"restaurantName":restaurantName,
		"productsChosen":productDetails,
		"subTotal":totalPrice,
		"totalAmt":totalAmount,
		"deliveryMin":deliveryMin,
		"deliveryPrice":deliveryPrice,
		"salesTax":salesTax,
		"isLoggedIn":isLoggedIn,
		"username":username})	

@persist_session_vars(['restaurants','dest_address','order_type','order_address','productsChosen','sectionNames','itemNameList','subTotal','salestax','totalAmt','deliveryPrice','deliveryMin','cities'])
def login(request, *args, **kwargs):
	print("it comes to this point")
	return views.login(request, *args, **kwargs)

def custom_login(request):
    if request.user.is_authenticated():
        return redirect('home')
    else:
        return login(request)

def profile(request):
	form = {}
	editName = False
	editEmail=False
	editPassWord = False

	if "isNameEdit" in request.session:
		editName = True
		form = EditNameForm(initial={'first_name':request.user.first_name , 'last_name': request.user.last_name})
		del request.session["isNameEdit"]

	if "isEmailEdit" in request.session:
		editEmail = request.session["isEmailEdit"]
		form = EditEmailForm()
		if editEmail == False:
			editEmail = True
			messages.add_message(request, messages.ERROR, 'Emails Do not Match')
		del request.session["isEmailEdit"]	
		
	fName = request.user.first_name
	lName = request.user.last_name
	email =  request.user.email

	print("editEmail in profile",editEmail)
	return render(request, 'Foodhubinit/profile.html',{
		"fName":fName,
		"lName":lName,
		"email":email,
		'form':form,
		'editName':editName,
		'editEmail':editEmail,
		'editPassWord':editPassWord
		})

def account(request):
	return render(request, 'Foodhubinit/account.html')


def getRestaurants(type,place):
	URL = "https://api.eatstreet.com/publicapi/v1/restaurant/search";
	URL+= "?method="+type+"&street-address="+urllib.parse.quote(place);
	req = urllib.request.Request(URL)
	req.add_header('X-Access-Token', '__API_EXPLORER_AUTH_KEY__')
	content = urllib.request.urlopen(req)
	contentReturned = content.read()
	encoding = content.info().get_content_charset('utf-8')
	JSON_object = json.loads(contentReturned.decode(encoding))
	return JSON_object['restaurants'];    

def find_restaurants(request,address):
	pageNum = request.GET.get('pageNum')
	orderType = "delivery"
	ratings =dict();
	sortBy = "default";
	if request.GET.get('orderType'):
		orderType = request.GET.get('orderType')

	if request.GET.get('sortBy'):
		sortBy = request.GET.get('sortBy')	

	restaurants = getRestaurants(orderType,address)


	print("sortBy here:",sortBy)
	print("type sortBy here:",type(sortBy))
	if sortBy!="default":
		restaurants.sort(key = lambda x: x[sortBy])

	request.session["restaurants"] = restaurants;
	request.session["dest_address"] = address;
	address_lat_long_resp = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+address)
	resp_json_payload = address_lat_long_resp.json()
	address_lat_long_resp = resp_json_payload['results'][0]['geometry']['location']
	cuisines = getCuisines(restaurants);
	request.session["order_type"] = orderType;
	displayRestaurants,page_range=getRestaurantDetails(restaurants,pageNum)
	print("restaurants here:",restaurants)
	request.session["isMenuPage"] =False



	return render(request, 'Foodhubinit/listRestaurants.html',
		{"restaurants":displayRestaurants,
		"ratings":ratings,
		"page_range":page_range,
		"cuisines":cuisines,
		"address":json.dumps(address),
		"orderTypeValue":json.dumps(orderType),
		"address_lat_long_resp":address_lat_long_resp,
		"sortBy":json.dumps(sortBy)})	

def getRestaurantDetails(restaurants,pageNum):
	paginator = Paginator(restaurants, 20)
	try:
		displayRestaurants = paginator.page(pageNum)
	except PageNotAnInteger:
		displayRestaurants = paginator.page(1)
	except EmptyPage:
		displayRestaurants = paginator.page(paginator.num_pages)

	index = displayRestaurants.number - 1 
	max_index = len(paginator.page_range)
	start_index = index - 2 if index >= 2 else 0
	end_index = index + 2 if index <= max_index - 2 else max_index
	page_range = paginator.page_range[start_index:end_index]
	return displayRestaurants,page_range

def getCuisines(restaurants):
	cuisines =dict()
	for restaurant in restaurants:
		for foodType in restaurant['foodTypes']:
			if foodType.lower() in cuisines:
				value = cuisines[foodType.lower() ]
				cuisines[foodType.lower()] = value + 1
			else:
				if foodType !='':
					cuisines[foodType.lower()] =1

	return cuisines


def object_compare(x, y):
   if x['deliveryMin'] > y['deliveryMin'] :
      return 1
   elif x['deliveryMin']  == y['deliveryMin'] :
      return 0
   else:  #x.resultType < y.resultType
      return -1	

def restaurant_description(request, restaurant_name):

	restaurantDesc =dict()
	restaurant_name = urllib.parse.unquote(restaurant_name)
	if "restaurants" in request.session:
		for restaurant in request.session["restaurants"]:
			if restaurant["name"] == restaurant_name:
				restaurantDesc = restaurant
				break

	print("restaurantDesc here:",restaurantDesc);
	menu= getRestaurantMenu(restaurantDesc['apiKey'])
	restaurantHoursUnsorted = restaurantDesc['hours']
	restaurantHours = dict();
	weekdays =["Sunday","Monday", "Tuesday", "Wednesday", "Thursday", "Friday","Saturday"]
	for day in weekdays:
		if day in restaurantHoursUnsorted:
			restaurantHours[day] = restaurantHoursUnsorted[day]
		else:
			restaurantHours[day] =["Holiday"]	

	address="";
	order_type ="delivery"
	productsChosen =list();
	sectionList = list();
	itemNameList = list();

	isLoggedIn =False
	fullName =""
	if request.user.is_authenticated():
		isLoggedIn = True
		fullName = request.user.get_full_name()

	if "order_address" in request.session:
		address = request.session["order_address"]
	elif "dest_address" in request.session:
		address = request.session["dest_address"]

	if request.session["order_type"]:
		order_type = request.session["order_type"]
	print("address here:",address)
	if order_type == "delivery":
		order_type ="Delivery"
	else:
		order_type ="Pick Up"

	if "productsChosen" in request.session:
		productsChosen = request.session["productsChosen"]

	if "sectionNames" in request.session:
		sectionList = request.session["sectionNames"]

	if "itemNameList" in request.session:
		itemNameList = request.session["itemNameList"]		

	print("productsChosen here:",productsChosen)
	print("sectionList here:",sectionList)
	print("itemNameList here:",itemNameList)

	totalPrice =0.000

	for product in productsChosen:
		totalPrice = totalPrice + (product['price']* product['qty'])
		if 'customizationList' in product:
			for customList in product['customizationList']:
				totalPrice += customList['price']

	print('subTotal:',totalPrice)
	totalValue =0.000
	totalPrice = round(totalPrice,3)
	request.session["subTotal"] = totalPrice
	request.session["salestax"] = restaurantDesc['taxRate']
	print("tax in cents:",((totalPrice*100)+ (restaurantDesc['taxRate'] * 100)))
	totalValue = round(((totalPrice*100) + (restaurantDesc['taxRate'] * 100))/100,3)
	print("totalValue here:",totalValue)
	request.session["totalAmt"] = totalValue

	request.session["deliveryPrice"] = restaurantDesc['deliveryPrice']

	productDetails =[]
	if len(productsChosen) !=0:
		productDetails = zip(productsChosen, sectionList, itemNameList)	

	print("productDetails:",productDetails)
	print("restaurantName:",restaurantDesc["name"])
	request.session["isMenuPage"] =True
	
	return render(request, 'Foodhubinit/restaurantPage.html',
		{"restaurant":restaurantDesc,
		"menus":menu,
		"restaurantHours":restaurantHours,
		"dest_address":address,
		"order_type":order_type,
		"productsChosen":productDetails,
		"restaurantName":restaurantDesc["name"],
		'subTotal':totalPrice,
		'salesTax':restaurantDesc["taxRate"],
		'deliveryPrice':restaurantDesc['deliveryPrice'],
		'totalAmt': request.session["totalAmt"],
		"isMenuPage":True,
		"isLoggedIn":isLoggedIn,
		"fullName":fullName})

def getRestaurantMenu(apiKey):
	URL = "https://api.eatstreet.com/publicapi/v1/restaurant/"+apiKey+"/menu";
	URL+= "?includeCustomizations=true";
	print("url here:",URL)
	req = urllib.request.Request(URL)
	req.add_header('X-Access-Token', '__API_EXPLORER_AUTH_KEY__')
	content = urllib.request.urlopen(req)
	contentReturned = content.read()
	encoding = content.info().get_content_charset('utf-8')
	JSON_object = json.loads(contentReturned.decode(encoding))
	return JSON_object;


def edit_name(request):

	user = request.user
	form = EditNameForm(request.POST or None, instance=user)
	if request.method == 'POST':
		print("it comes inside post request")
		if form.is_valid():
			print('Form is valid')

			user.first_name = request.POST['first_name']
			user.last_name = request.POST['last_name']
			print("it comes inside form")

			user.save()
			return HttpResponseRedirect('%s'%(reverse('account')))

	else:
		request.session['isNameEdit'] = True
		return redirect('account')
	# return render(request, 'Foodhubinit/profile.html', {'form': form,'editForm':True})

def edit_email(request):
	user = request.user
	form = EditEmailForm(request.POST or None, instance=user)
	if request.method == 'POST':
		print("it comes inside post request")
		if form.is_valid():
			user.email = request.POST['email']
			user.save()
			return HttpResponseRedirect('%s'%(reverse('account')))
		else:
			request.session['isEmailEdit'] = False
			return redirect('account')	
	else:
		request.session['isEmailEdit'] = True
		return redirect('account')			