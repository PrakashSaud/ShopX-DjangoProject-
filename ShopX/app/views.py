
from math import prod
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from .models import Customer, Product, Cart, OrderPlaced
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
import random


# VIEWs for Products
class ProductView(View):
    def get(self, request):
        gins = Product.objects.filter(category='GN')
        rums = Product.objects.filter(category='RM')
        tequilas = Product.objects.filter(category='TQ')
        vodkas = Product.objects.filter(category='VK')
        whiskeys = Product.objects.filter(category='WS')
        wines = Product.objects.filter(category='WN')
        return render(request, 'app/home.html', {
            'gins':gins,
            'rums':rums,
            'tequilas':tequilas,
            'vodkas':vodkas,
            'whiskeys':whiskeys,
            'wines':wines,
        })

class ProductDetailView(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        discounted_price = product.get_discounted_price()
        # To make if item is already in cart then show go to cart
        item_already_in_cart = False
        if request.user.is_authenticated:
            item_already_in_cart = Cart.objects.filter(Q(product=product.id) and Q(user=request.user)).exists()

        return render(request, 'app/productdetail.html', {'product':product, 'discounted_price': discounted_price, 'item_already_in_cart':item_already_in_cart})

def wine(request, data=None):
    if data == None:
        wines = Product.objects.filter(category='WN')
    elif data == 'wine' or data == 'sauvgnon_blanc' :
        wines = Product.objects.filter(category='WN').filter(brand=data.replace("_", " ").capitalize())
    elif data == 'below':
        wines = Product.objects.filter(category='WN').filter(selling_price__lt=20)
    elif data == 'above':
        wines = Product.objects.filter(category='WN').filter(selling_price__gt=20)
    return render(request, 'app/wines.html', {'wines': wines})

def gin(request, data=None):
    if data == None:
        gins = Product.objects.filter(category='GN')
    elif data == 'Gin' or data == '':
        gins = Product.objects.filter(category='GN').filter(brand=data)
    elif data == 'below':
        gins = Product.objects.filter(category='GN').filter(selling_price__lt=20)
    elif data == 'above':
        gins = Product.objects.filter(category='GN').filter(selling_price__gt=20)
    return render(request, 'app/gin.html', {'gins': gins})

def rum(request, data=None):
    if data == None:
        rums = Product.objects.filter(category='RM')
    elif data == 'Rum' or data == '':
        rums = Product.objects.filter(category='RM').filter(brand=data)
    elif data == 'below':
        rums = Product.objects.filter(category='RM').filter(selling_price__lt=20)
    elif data == 'above':
        rums = Product.objects.filter(category='RM').filter(selling_price__gt=20)
    return render(request, 'app/rum.html', {'rums': rums})

def tequila(request, data=None):
    if data == None:
        tequilas = Product.objects.filter(category='TQ')
    elif data == 'below':
        tequilas = Product.objects.filter(category='TQ').filter(selling_price__lt=20)
    elif data == 'above':
        tequilas = Product.objects.filter(category='TQ').filter(selling_price__gt=20)
    return render(request, 'app/tequila.html', {'tequilas': tequilas})

def whiskey(request, data=None):
    if data == None:
        whiskeys = Product.objects.filter(category='WS')
    elif data == 'below':
        whiskeys = Product.objects.filter(category='WS').filter(selling_price__lt=20)
    elif data == 'above':
        whiskeys = Product.objects.filter(category='WS').filter(selling_price__gt=20)
    return render(request, 'app/whiskey.html', {'whiskeys': whiskeys})
    

# Customer Registration    
class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form':form})   
    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Congratulations!! Registered Successfully')
            form.save()
        return render(request, 'app/customerregistration.html', {'form':form})


# Profile related views
@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary'})
    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            address = form.cleaned_data['address']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']

            reg = Customer(user=usr, name=name, address=address, city=city, state=state, zipcode=zipcode)
            reg.save()
            messages.success(request, "Congratulations!! Profile Updated Successfully")
        return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary'})

@login_required
def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html', {'add':add, 'active':'btn-primary'})


# cart related views
@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return redirect('/cart')

@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user)
        # discounted_price = cart.product.selling_price - cart.product.selling_price * cart.product.discount_percent / 100
        amount = 0.0
        total_discount = 0.0
        delivery_charge = 0.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user==user]
        if cart_product:
            for p in cart_product:
                temp_discount = p.product.get_discount_amount()
                total_discount += temp_discount
                temp_amount = (p.quantity * p.product.selling_price)
                amount += temp_amount
            total_amount = amount + delivery_charge - total_discount
            tax_amount = 8.875 * amount / 100
            total_amount += tax_amount
            return render(request, 'app/showcart.html', {'cart':cart, 'totalamount':total_amount, 'amount':amount, 'deliverycharge':delivery_charge, 'taxamount':tax_amount, 'discount':total_discount})
        
        else:
            return render(request, 'app/emptycart.html')

def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id)) & Q(user=request.user)
        c.quantity += 1
        c.save()
        amount = 0.0
        total_discount = 0.0
        delivery_charge = 0.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            temp_discount = p.product.selling_price * p.product.discount_percent / 100
            total_discount += temp_discount
            temp_amount = (p.quantity * p.product.selling_price)
            amount += temp_amount
            total_amount = amount + delivery_charge
        tax_amount = 8.875 * amount / 100
        total_amount += tax_amount
        data = {
            'quantity':c.quantity,
            'totalamount':total_amount, 'amount':amount, 'deliverycharge':delivery_charge, 'taxamount':tax_amount, 'discount':total_discount
        }
        return JsonResponse(data)

def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id)) & Q(user=request.user)
        c.quantity -= 1
        c.save()
        amount = 0.0
        total_discount = 0.0
        delivery_charge = 0.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            temp_discount = p.product.selling_price * p.product.discount_percent / 100
            total_discount += temp_discount
            temp_amount = (p.quantity * p.product.selling_price)
            amount += temp_amount
            total_amount = amount + delivery_charge
        tax_amount = 8.875 * amount / 100
        total_amount += tax_amount
        data = {
            'quantity':c.quantity,
            'totalamount':total_amount, 'amount':amount, 'deliverycharge':delivery_charge, 'taxamount':tax_amount, 'discount':total_discount
        }
        return JsonResponse(data)

def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id)) & Q(user=request.user)
        c.delete()
        amount = 0.0
        total_discount = 0.0
        delivery_charge = 0.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            temp_discount = p.product.selling_price * p.product.discount_percent / 100
            total_discount += temp_discount
            temp_amount = (p.quantity * p.product.selling_price)
            amount += temp_amount
            total_amount = amount + delivery_charge
        tax_amount = 8.875 * amount / 100
        total_amount += tax_amount
        data = {
            'totalamount':total_amount, 'amount':amount, 'deliverycharge':delivery_charge, 'taxamount':tax_amount, 'discount':total_discount
        }
        return JsonResponse(data)

@login_required
def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = 0.0
    total_discount = 0.0
    delivery_charge = 0.0
    total_amount = 0.0
    cart_product = [p for p in Cart.objects.all() if p.user==user]
    if cart_product:
        for p in cart_product:
            temp_discount = p.product.get_discount_amount()
            total_discount += temp_discount
            temp_amount = (p.quantity * p.product.selling_price)
            amount += temp_amount
        total_amount = amount + delivery_charge - total_discount
        tax_amount = 8.875 * amount / 100
        total_amount += tax_amount

    return render(request, 'app/checkout.html', {'add':add, 'totalamount':total_amount, "cart_items":cart_items})


@login_required
def payment_done(request):
    user = request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user, customer=customer, product = c.product, quantity = c.quantity).save()
        c.delete()
    return redirect('orders')


def buy_now(request):
 return render(request, 'app/buynow.html')

@login_required
def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html', {'order_placed':op})