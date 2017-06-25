from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode,  urlsafe_base64_decode
from django.template.loader import render_to_string
import json
from bson import json_util
from bson.json_util import dumps
import urllib.request,urllib.parse
import requests
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import collections
import operator

from Foodhubinit.forms import SignUpForm
from Foodhubinit.tokens import account_activation_token
import json


# Create your views here.

def index(request):
	json_data = open('Foodhubinit/static/Foodhub/json/us_state_capitals.json')
	data1 = json.load(json_data)
	capitals =list()
	request.session['cities'] = {}
	request.session.modified = True
	
	for attribute, value in data1.items():
		capitals.append(value['capital'])
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

def cities(request,state_name):
	json_data = open('Foodhubinit/static/Foodhub/json/cities.json')
	data = json.load(json_data)
	cities = list();
	for cityObj in data:
		if cityObj['state'] == state_name:
			cities.append(cityObj['city'])

	print("citiesNew:",cities)
	# json_data = open('Foodhubinit/static/Foodhub/json/counties.json')
	# data1 = json.load(json_data)
	# cities = data1.get(state_name)
	request.session["cities"] = cities
	return render(request, 'Foodhubinit/listAllCities.html',{"cities":cities})

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
	return render(request, 'Foodhubinit/listCityRestaurants.html',{"city":city_name,"nearby_cities":nearbyCities,"restaurants":displayRestaurants,"total":totalRestaurants,"ratings":ratings,"page_range":page_range})	

def custom_login(request):
    if request.user.is_authenticated():
        return redirect('home')
    else:
        return login(request)


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

	return render(request, 'Foodhubinit/listRestaurants.html',{"restaurants":displayRestaurants,"ratings":ratings,"page_range":page_range,"cuisines":cuisines,"address":json.dumps(address),"orderTypeValue":json.dumps(orderType),"address_lat_long_resp":address_lat_long_resp,"sortBy":json.dumps(sortBy)})	

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
	if request.session["restaurants"]:
		for restaurant in request.session["restaurants"]:
			if restaurant["name"] == restaurant_name:
				restaurantDesc = restaurant
				break

	menu= getRestaurantMenu(restaurantDesc['apiKey'])
	restaurantHoursUnsorted = restaurantDesc['hours']
	restaurantHours = dict();
	weekdays =["Sunday","Monday", "Tuesday", "Wednesday", "Thursday", "Friday","Saturday"]
	for day in weekdays:
		restaurantHours[day] = restaurantHoursUnsorted[day];

	address="";
	order_type ="delivery"
	productsChosen =list();
	sectionList = list();
	itemNameList = list();

	if request.session["dest_address"]:
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
	productDetails =[]
	if len(productsChosen) !=0:
		productDetails = zip(productsChosen, sectionList, itemNameList)	

	print("productDetails:",productDetails)
	
	return render(request, 'Foodhubinit/restaurantPage.html',{"restaurant":restaurantDesc,"menus":menu,"restaurantHours":restaurantHours,"dest_address":address,"order_type":order_type,"productsChosen":productDetails})
	pass

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


