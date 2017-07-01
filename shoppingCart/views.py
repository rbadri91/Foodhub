from django.shortcuts import render
from django.http import HttpResponse
import ast
import json
from bson import json_util
from bson.json_util import dumps

# Create your views here.

def showCart(request):
	pass

def addToCart(request):
	productsChosen = list();
	sectionList = list();
	itemNameList = list();

	chosenProductDetails = ast.literal_eval(request.POST["productDetails"])
	
	if "productsChosen" in request.session:
		productsChosen = request.session["productsChosen"]

	productsChosen.append(chosenProductDetails);
	request.session["productsChosen"] = productsChosen

	print("product chosen session:",request.session["productsChosen"])

	if "sectionNames" in request.session:
		sectionList = request.session["sectionNames"]

	sectionList.append(request.POST["sectionName"]);
	request.session["sectionNames"] = sectionList

	if "itemNameList" in request.session:
		itemNameList = request.session["itemNameList"]

	itemNameList.append(request.POST["itemName"]);
	request.session["itemNameList"] = itemNameList

	request.session["restaurantName"] = request.POST["restaurantName"]

	request.session["order_address"] = request.session["dest_address"]

	request.session["deliveryMin"] = request.POST["deliveryMin"]
	request.session["deliveryPrice"] = request.POST["deliveryPrice"]

	totalPrice =0
	subPrice=0;


	if "subTotal" in request.session:
		totalPrice = request.session["subTotal"]

	subPrice += chosenProductDetails['price'];
	if 'customizationList' in chosenProductDetails:
		for customList in chosenProductDetails['customizationList']:
			subPrice += customList['price']	

	totalPrice +=(subPrice * chosenProductDetails['qty'])
	totalPrice = round(totalPrice,3)
	print('totalPrice here:',totalPrice)
	totalAmt =0
	taxAmt =0.0;
	deliveryMin =0.0;

	
	if 'totalAmt' in request.session:
		totalAmount = request.session["totalAmt"]

	totalAmount += (subPrice * chosenProductDetails['qty']);
	request.session["totalAmt"] = round(totalAmount,3)
	request.session["subTotal"] = totalPrice

	if 'salesTax' in request.session:
		taxAmt = request.session["salesTax"]

	print("sectionNames session:",request.session["sectionNames"])
	print("itemNameList session:",request.session["itemNameList"])

	priceInfo ={"totalAmt":request.session["totalAmt"],"subTotal":request.session["subTotal"],"taxAmt":taxAmt,"deliveryFee":request.session["deliveryPrice"]}
	return HttpResponse(json.dumps(priceInfo), content_type="application/json")

def removeFromCart(request):
	productsChosen = list();
	sectionList = list();
	itemNamesList = list();

	totalPrice =0

	if "subTotal" in request.session:
		totalPrice = request.session["subTotal"] 

	totalAmount =0

	if 'totalAmt' in request.session:
		totalAmount = request.session["totalAmt"]			

	if "productsChosen" in request.session:
		productsChosen = request.session["productsChosen"]

	print("productsChosen session :", productsChosen)	

	for idx, product in enumerate(productsChosen):
		print("product  :", product)
		print("idx  :", idx)	
		if product['name'] == request.POST["productName"]:
			productDeleted = productsChosen[idx]
			subPrice = productDeleted['price']
			
			if 'customizationList' in productDeleted:
				for customList in productDeleted['customizationList']:
					subPrice +=customList['price']
			
			totalPrice -= (subPrice * productDeleted['qty'])
			totalPrice = round(totalPrice,3)
			request.session["subTotal"] = totalPrice
			totalAmount -= (subPrice * productDeleted['qty']);
			totalAmount = round(totalAmount,3)
			request.session["totalAmt"] = totalAmount

			del  productsChosen[idx]

	

	if "sectionNames" in request.session:
		sectionList = request.session["sectionNames"]

	
	if 	request.POST["sectionName"] in sectionList:
		sectionList.remove(request.POST["sectionName"])	

	if "itemNameList" in request.session:
		itemNamesList = request.session["itemNameList"]

	if 	request.POST["itemName"] in itemNamesList:
		itemNamesList.remove(request.POST["itemName"])

	request.session["productsChosen"] = productsChosen
	request.session["sectionNames"] = sectionList
	request.session["itemNameList"] = itemNamesList

	print("productsChosen session:",request.session["productsChosen"])
	print("sectionNames session:",request.session["sectionNames"])
	print("itemNameList session:",request.session["itemNameList"])
	isMenuPage = False
	if "isMenuPage" in request.session:
		isMenuPage = request.session["isMenuPage"]

	if len(request.session["productsChosen"]) ==0:
		restaurantInfo = {"isMenuPage":isMenuPage,"restautantName":request.session["restaurantName"],"deliveryMin":request.session["deliveryMin"],"deliveryPrice":request.session["deliveryPrice"],"subTotal":totalPrice,"totalAmt":totalAmount}
	else:
		restaurantInfo = {"isMenuPage":isMenuPage,"restautantName":request.session["restaurantName"],"subTotal":totalPrice,"totalAmt":totalAmount}	
	
	return HttpResponse(json.dumps(restaurantInfo), content_type="application/json")



