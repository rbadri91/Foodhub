from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from decimal import Decimal

import json
import pprint
import urllib
import stripe

from .actions import sources,charges,customers

# Create your views here.

@login_required
def confirmOrder(request):
	username = request.user.username
	firstName = request.user.first_name;
	lastName = request.user.last_name;
	email= request.user.email;
	addresses = request.user.profile.addresses
	print("firstName here:",firstName)
	print("lastName here:",lastName)
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

	city_name ="", 
	state_name ="NY", 
	zip_code =12345
	# city_name, state_name, zip_code = getSplitAddress(address)

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

				
	request.session["isMenuPage"] =True
	print('address here:',address)

	issavedAddress = False

	if address in addresses:
		issavedAddress = True

	print("issavedAddress here:",issavedAddress)	

	return render(request,'orders/orderConfirm.html',
		{
			"order_type":order_type,
			"dest_address":address,
			"restaurantName":restaurantName,
			"productsChosen":productDetails,
			"subTotal":totalPrice,
			"totalAmt":totalAmount,
			"deliveryMin":deliveryMin,
			"deliveryPrice":deliveryPrice,
			"salesTax":salesTax,
			"username":username,
			"firstName":firstName,
			"lastName":lastName,
			"isMenuPage":True,
			"email":email,
			"city_name":city_name,
			"state_name":state_name,
			"zip_code":zip_code,
			"issavedAddress":issavedAddress,
			"isOrderConfirmPage":True
		})

def getSplitAddress(address):
	LOCATION = 'https://api.qualifiedaddress.com/street-address/'
	QUERY_STRING = urllib.parse.urlencode({ # entire query sting must be URL-Encoded
	    'auth-token': r'0UfFF7wVSDLg0SyCMNxq',
	    'street': address
	})
	URL = LOCATION + '?' + QUERY_STRING

	response = urllib.request.urlopen(URL).read()
	structure = json.loads(response)
	pprint.pprint(structure)
	return structure["city_name"],structure["state_abbreviation"], structure["zipcode"]

@login_required
def saveAddress(request):
	address = request.POST['address']
	print("address here:",address)
	if not address in request.user.profile.addresses:
		request.user.profile.addresses.append(address)
		print("in if check")
	else:
		request.user.profile.addresses.remove(address)
		print("in else check")	
	
	request.user.profile.save()
	return HttpResponse("success")

@login_required
def orderPayment(request):
	firstName = request.user.first_name;
	lastName = request.user.last_name;
	return render(request,'orders/orderPayment.html',{
		"firstName":firstName,
		"lastName":lastName,
	})

@login_required
def chargeCard(request):
	stripe.api_key = "sk_test_zxRWFSiVXfdaMAEbtDFFrSTw"
	token = request.POST.get("stripeToken")
	print("it comes inside")
	print("token here:",token)
	# customer = customers.get_customer_for_user(request.user)
	# print("customer here:",customer)
	# sources.create_card(customer,token)

	customer = stripe.Customer.create(
	  email=request.user.email,
	  source=token,
	)

	charges.create(amount=Decimal("1500"), description="Example charge",customer=customer, send_receipt=False)
	
	restaurants = request.session["restaurants"]
	print("restaurants here:",restaurants)

	return render(request,'orders/paymentConfirm.html');


