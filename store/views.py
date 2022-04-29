from datetime import datetime
from email import message
from django.contrib import messages
import json
from django.http import JsonResponse
from django.shortcuts import redirect, render
from .models import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.paginator import Paginator

# Create your views here.



def loginPage(request):
    print(request)
    if request.user.is_authenticated:
        return redirect('store')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user,  backend=None)
            return redirect('store')
        else:
            messages.error(request, 'Username Or Password are not correct!')

    return render(request, 'store/login.html')

def registerPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = User.objects.create_user(username, email, password)
        if user is not None:
            user.save()
            customer = Customer(user=user, name=username, email=email)
            customer.save()
            login(request, user)
            return redirect('store')
        else:
            messages.error(request, 'An error occuers')
    return render(request, 'store/register.html')

def logoutUser(request):
    logout(request)
    return redirect('store')

def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items   
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']
    
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    print(q)
    categories = Category.objects.all()
    products = Product.objects.filter(Q(category__name__icontains=q))
    p = Paginator(products, 6)
    page_number = request.GET.get('page')
    page_obj = p.get_page(page_number)
    num = 'a' * page_obj.paginator.num_pages
    context = { 'products': products, 'cartItems': cartItems, 'categories': categories, 'page_obj': page_obj, 'num': num}
    return render(request, 'store/store.html', context)

@login_required(login_url='/login/')
def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']
    context = { 'items': items, 'order': order , 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)

@login_required(login_url='/login/')
def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/check.html', context)

@csrf_exempt
@login_required(login_url='/login/')
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

@login_required(login_url='/login/')
def processOrder(requset):
    transaction_id = datetime.now().timestamp()
    data = json.loads(requset.body)

    if requset.user.is_authenticated:
        customer = requset.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = data['form']['total']
        order.transaction_id = transaction_id
        
        if total == order.get_cart_total:
            order.complete = True
        order.save()

        if order.shipping == True:
            ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            country=data['shipping']['country'],
            zipcode=data['shipping']['zipcode'],
            )
    else:
        print("user is logouted")
    return JsonResponse('Payment submitted..', safe=False)