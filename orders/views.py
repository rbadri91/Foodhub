from django.shortcuts import render
from django.contrib.auth.decorators import login_required

import json
import pprint
import urllib

# Create your views here.

@login_required
def confirmOrder(request):
	username = request.user.username
	firstName = request.user.first_name;
	lastName = request.user.last_name;
	email= request.user.email;
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
