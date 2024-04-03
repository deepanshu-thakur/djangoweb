from django.shortcuts import render, redirect
from books.models import Book
from django.contrib.auth.decorators import login_required
from cart.cart import Cart

@login_required(login_url="/users/login")
def cart_add(request, id):
    cart = Cart(request)
    product = Book.objects.get(id=id)
    cart.add(product=product)
    return redirect("/cart/cart-detail")


@login_required(login_url="/users/login")
def item_clear(request, id):
    cart = Cart(request)
    product = Book.objects.get(id=id)
    cart.remove(product)
    return redirect("/cart/cart-detail")


@login_required(login_url="/users/login")
def item_increment(request, id):
    cart = Cart(request)
    product = Book.objects.get(id=id)
    cart.add(product=product)
    return redirect("/cart/cart-detail")


@login_required(login_url="/users/login")
def item_decrement(request, id):
    cart = Cart(request)
    product = Book.objects.get(id=id)
    cart.decrement(product=product)
    return redirect("/cart/cart-detail")


@login_required(login_url="/users/login")
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("/cart/cart-detail")


@login_required(login_url="/users/login")
def cart_detail(request):
    return render(request, 'books/cart.html')


