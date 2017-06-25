from django.shortcuts import render
from django.http import HttpResponse
import ast

# Create your views here.

def showCart(request):
	pass

def addToCart(request):
	productsChosen = list();
	sectionList = list();
	itemNameList = list();
	
	if "productsChosen" in request.session:
		productsChosen = request.session["productsChosen"]

	productsChosen.append(ast.literal_eval(request.POST["productDetails"]));
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

	print("sectionNames session:",request.session["sectionNames"])
	print("itemNameList session:",request.session["itemNameList"])
	return HttpResponse("Succesfully added")

def removeFromCart(request):
	productsChosen = list();
	sectionList = list();
	itemNamesList = list();


	if "productsChosen" in request.session:
		productsChosen = request.session["productsChosen"]

	print("productsChosen session :", productsChosen)	

	for idx, product in enumerate(productsChosen):
		print("product  :", product)
		print("idx  :", idx)	
		if product['name'] == request.POST["productName"]:
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
	return HttpResponse("Succesfully Removed")



