# Foodhub

This is a web application built entirly using Python, Django web framework, and Postgres to help people locate a good restaurant nearby and order food to either get it deliverd or picjked up. I am using EatStreet API for getting information about the restaurant s which include the restaurant timings and menu details.

This project consists of 3 internal applications

Foodhubinit: An application that holds the user model and contains templates for landing pages and for listing restaurants

shoppingCart: As the name suggests it contains everything related to shopping cart such as adding , reoving and updating products.

orders: It contains teamplates for showig user their final order datails and viewing formas relevant to payment. It contains procedures to store information about order details for which a separate table in PostgreSQL has been created.

Database Tables:
Profile: 
```
user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)
    phone_no = USPhoneNumberField(required=False, label="Phone")
    addresses = ArrayField(models.CharField(max_length=200, blank=True),default=list, null=True)
```
The profile database contais information on user , like phone number ans saved addresses. This is queried to get information about the past addresses

Order:
```
order_id = models.CharField(max_length=120, default=uuid.uuid4, unique=True, primary_key=True)
    	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    	delivery_address = models.CharField(max_length=200, blank=True)
    	order_Desc= ArrayField(JSONField(),default=list, null=True);
    	order_by = models.ForeignKey(User,null=True, blank=True,on_delete=models.CASCADE);
```
  The order table contains information on the orders placed , the time, the delivery address if it is a delivery type of order, and the user who ordered it
  
  Card:
 ```
 customer = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.TextField(blank=True)
    address_line_1 = models.TextField(blank=True)
    address_line_1_check = models.CharField(max_length=15)
    address_line_2 = models.TextField(blank=True)
    address_city = models.TextField(blank=True)
    address_state = models.TextField(blank=True)
    address_country = models.TextField(blank=True)
    address_zip = models.TextField(blank=True)
    address_zip_check = models.CharField(max_length=15)
    country = models.CharField(max_length=2, blank=True)
    cvc_check = models.CharField(max_length=15, blank=True)
    dynamic_last4 = models.CharField(max_length=4, blank=True)
    tokenization_method = models.CharField(max_length=15, blank=True)
    exp_month = models.IntegerField()
    exp_year = models.IntegerField()

 ```
 The card table contains alll the information about the card used by the user
  
The cart details are sored in session as it will be cleared once a user has logged out and has not proceed to order food.

Stripe API is used to for payment processing.

This app thas been tested with valid test card details provoided by stripe.
Django Template is used for the front end and Bootstrap is used to beautify the web pages. 

To run the app you have to create a database in postgres / MYSQL or d3sql .I have used Postgres to address scalability issues,either Python 2.7 or 3.6 and the latestversion od Django 1.11.

