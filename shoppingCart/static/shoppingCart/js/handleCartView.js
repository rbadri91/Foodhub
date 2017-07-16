
function constructProductContainer(productDetails,sectionName,itemName){

	var prodMenuContainer = document.getElementById("menuOrderCart");
	if(!prodMenuContainer){
		prodMenuContainer =  document.createElement("div");
		prodMenuContainer.className = "productsContainer";
		prodMenuContainer.id = "menuOrderCart";
		document.getElementById("cartPanel").appendChild(prodMenuContainer);
	}
	var productContainer = document.createElement("div");
	productContainer.className = "chosenProd cart-borderbottom";
	productContainer.id = productDetails.name +"container";
	prodMenuContainer.appendChild(productContainer);
	var prodQty = document.createElement("div");
	prodQty.className = "prodQty text-center";
	prodQty.textContent =productDetails.qty;
	productContainer.appendChild(prodQty);
	var productInnerContainer = document.createElement("div");
	productInnerContainer.className = "chosenprodContainer";
	productContainer.appendChild(productInnerContainer);
	var prodName = document.createElement("div");
	prodName.className ="prodName";
	productInnerContainer.appendChild(prodName);
	var nameSpan = document.createElement("span");
	nameSpan.textContent =  productDetails.name;
	prodName.appendChild(nameSpan);
	prodName.style.cursor="pointer";
	var itemEdit = document.createElement("i");
	itemEdit.className ="fa fa-pencil-square-o";
	itemEdit.setAttribute("aria-hidden","true");
	prodName.appendChild(itemEdit);
	var prodDescription = document.createElement("ul");
	productInnerContainer.appendChild(prodDescription);
	for(var i=0;i<productDetails.customizationList.length;i++){
		var productCustomization = document.createElement("li");
		productInnerContainer.appendChild(productCustomization);
		var customizationName = document.createElement("span");
		customizationName.textContent = productDetails.customizationList[i].name;
		productCustomization.appendChild(customizationName);
		if(productDetails.customizationList[i].price!=0){
			var customizationPrice = document.createElement("span");
			customizationPrice.textContent =" - $" + productDetails.customizationList[i].price;
			productCustomization.appendChild(customizationPrice);
		}
	}
	var prodPrice = document.createElement("div");
	prodPrice.className ="product-price text-center";
	prodPrice.textContent = "$"+productDetails.price;
	productContainer.appendChild(prodPrice);
	var prodRemove = document.createElement("div");
	prodRemove.className ="prod-remove";
	productContainer.appendChild(prodRemove);
	var prodRemoveButton = document.createElement("a");
	prodRemoveButton.id = productDetails.name+"delete_"+ sectionName +"_"+itemName;
	$(prodRemoveButton).bind( "click", function() {
		handleRemoveProduct(this);
	});
	prodRemove.appendChild(prodRemoveButton);
	prodRemoveButton.style.fontSize ="150%";
	var removeIcon = document.createElement("i");
	removeIcon.className = "fa fa-trash-o";
	removeIcon.setAttribute("aria-hidden","true");
	prodRemoveButton.appendChild(removeIcon);
}

function constructEmptyCartContainer(isMenuPage,delPrice,delMin){
	var cartContainer = document.createElement("div");
	cartContainer.id = "cartEmptyContainer";
	cartContainer.className = "cartEmpty text-center";
	document.getElementById("cartPanel").appendChild(cartContainer);
	var emptyCartHeder =document.createElement("div");
	emptyCartHeder.id="cart-empty cart-borderbottom";
	cartContainer.appendChild(emptyCartHeder); 
	var emptyCartHeaderText = document.createElement("h5");
	emptyCartHeaderText.className = "emptyCart-text";
	emptyCartHeaderText.textContent = "Your Cart is Empty";
	cartContainer.appendChild(emptyCartHeaderText);
	if(isMenuPage){
		var restaurantFeeInfo = document.createElement("div");
		restaurantFeeInfo.className = "restaurantfees";
		cartContainer.appendChild(restaurantFeeInfo);
		var restaurantDeliveryCostContainer = document.createElement("div");
		restaurantDeliveryCostContainer.className = "minDeliveryCost cart-borderbottom";
		restaurantFeeInfo.appendChild(restaurantDeliveryCostContainer);
		var deliveryCostHeader = document.createElement("span");
		deliveryCostHeader.textContent = "Delivey Cost";
		restaurantDeliveryCostContainer.appendChild(deliveryCostHeader);
		var deliveryCostValue = document.createElement("span");
		deliveryCostValue.className ="costValue";

		if(delPrice ==0.0){
			deliveryCostValue.textContent ="Free";
		}else{
			deliveryCostValue.textContent = delPrice;
		}
		restaurantDeliveryCostContainer.appendChild(deliveryCostValue);

		var restaurantDeliveryMinContainer = document.createElement("div");
		restaurantDeliveryMinContainer.className = "minDeliveryCost cart-borderbottom";
		restaurantFeeInfo.appendChild(restaurantDeliveryMinContainer);
		var deliveryCostHeader = document.createElement("span");
		deliveryCostHeader.textContent = "Minimum Order";
		restaurantDeliveryMinContainer.appendChild(deliveryCostHeader);
		var deliveryMinValue = document.createElement("span");
		deliveryMinValue.className ="costValue";
		deliveryMinValue.textContent ="$"+delMin;
		restaurantDeliveryMinContainer.appendChild(deliveryMinValue);
	}

}
function createSubTotalWrapper(subTotal,deliveryFee,taxAmt,total){
	var subTotalWrapper = document.createElement('div');
	subTotalWrapper.id ="subTotalWrapper";
	subTotalWrapper.className ="subTotalContainer";
	document.getElementById("cartPanel").appendChild(subTotalWrapper);
	constructSubTotalRow(subTotalWrapper,"ProductSubTotal","Items Subtotal:",subTotal);
	constructSubTotalRow(subTotalWrapper,"","Delivery Fee:",deliveryFee);
	constructSubTotalRow(subTotalWrapper,"","Sales Tax:",taxAmt);
	constructSubTotalRow(subTotalWrapper,"ProductTotal","Total:",total);
}

function constructSubTotalRow(subTotalWrapper,divId,labelName,value){
	var itemDescription = document.createElement("div");
		itemDescription.className ="s-row chosenItem subtotalDescription";
		subTotalWrapper.appendChild(itemDescription);
	var itemLabel = document.createElement("div");
		itemLabel.className ="chosenItemLabel";
		itemDescription.appendChild(itemLabel);
	var lableSpan = document.createElement("span");	
		lableSpan.textContent = labelName;
		itemLabel.appendChild(lableSpan);
	var itemValueWrapper = 	document.createElement("div");
		itemValueWrapper.id =divId;
		itemValueWrapper.className ="chosenItemValue text-right";
		if(value !=0.0){
			itemValueWrapper.textContent = "$" + value;
		}else{
			itemValueWrapper.textContent = "Free";
		}
		
	itemDescription.appendChild(itemValueWrapper);

}

function createCartFooter(totalValue){
	var cartFooter = document.createElement("div");
		cartFooter.className ="cartFooter";
		cartFooter.id ="cartFooterContainer";
	document.getElementById("cartPanelContainer").appendChild(cartFooter);
	var proceedButtonContainer = document.createElement("div");
	proceedButtonContainer.className = "proceedButtonContainer";
	cartFooter.appendChild(proceedButtonContainer);
	var proceedButtonWrapper = document.createElement("div");
	proceedButtonWrapper.className = "proceedButtonWrapper";
	proceedButtonContainer.appendChild(proceedButtonWrapper);
	var proceedButton = document.createElement("button");
	proceedButton.className = "btn proceedButton f-btn f-btn-full btn-info";
	proceedButtonWrapper.appendChild(proceedButton);
	var proceedButtonLabel = document.createElement("span");
	proceedButtonLabel.textContent ="Proceed To Checkout";
	proceedButton.appendChild(proceedButtonLabel);
	var proceedButtonValue = document.createElement("span");
	proceedButtonValue.id = "totalValue";
	proceedButtonValue.textContent ="$ "+ totalValue;
	proceedButton.appendChild(proceedButtonValue);
}

function handleOrderType(el){
	if(el.id =="delivery"){
		activeOrderType ="Delivery";
		$("#PickUp").removeClass("f-btn-active");
		$("#delivery").addClass("f-btn-active");
		if(document.getElementById('address_holder')){
			document.getElementById('address_holder').style.display="block";
			document.getElementById('save_addressBox').style.display="block";
		}
	}else{
		activeOrderType ="Pick Up";
		$("#PickUp").addClass("f-btn-active");
		$("#delivery").removeClass("f-btn-active");
		if(document.getElementById('address_holder')){
			document.getElementById('address_holder').style.display="none";
			document.getElementById('save_addressBox').style.display="none";
		}
	}
}
function handleCartClick(){
	// console.log("in handleCartClick");
	$( "#cartContainer" ).toggle("slide",{ direction: "right" });
}