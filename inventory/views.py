from typing import Counter
from django import http
from django.core import paginator
from django.shortcuts import render, redirect
from django.http import HttpResponse, request
from django.contrib import messages
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import re
import os
import math
import datetime
from datetime import timedelta
from django.contrib.auth.models import User, auth
from .models import cat, product, sell, accounts
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.cache import cache  # This is the memcache cache.
from django.db.models import Sum


from django import template

register = template.Library()


@register.filter
def cool_number(value, num_decimals=2):
    """
    Django template filter to convert regular numbers to a
    cool format (ie: 2K, 434.4K, 33M...)
    :param value: number
    :param num_decimals: Number of decimal digits
    """

    int_value = int(value)
    formatted_number = '{{:.{}f}}'.format(num_decimals)
    if int_value < 1000:
        return str(int_value)
    elif int_value < 1000000:
        return formatted_number.format(int_value/1000.0).rstrip('0.') + 'K'
    else:
        return formatted_number.format(int_value/1000000.0).rstrip('0.') + 'M'


# authenticaition start
# login


def index(request):

    if request.user.is_authenticated:
        account = accounts.objects.filter(id=1)

        if account.exists():
            return redirect('inventory')
        else:
            accounts.objects.create()

        return redirect('inventory')

    if request.method == 'POST':
        name = request.POST['uname']
        password = request.POST['password']

        user = auth.authenticate(username=name, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("inventory")
        else:
            messages.info(request, "Invalid username or password")
            return redirect("/")

    else:
        return render(request, 'index.html')


# logout
def logout(request):
    cache.clear()
    auth.logout(request)
    return redirect('/')


# authentication end


def inventory(request):
    if request.user.is_authenticated:
        acc = accounts.objects.all()[0]
        total_cat = cat.objects.all().count()
        total_product = product.objects.all().count()
        total_sales = sell.objects.all().count()
        total_delivered = sell.objects.filter(delivered=True).count()
        contex = {
            'total_cat': total_cat,
            'total_sales': total_sales,
            'total_product': total_product,
            'total_delivered': total_delivered,
        }
        start_date = datetime.date.today() - timedelta(days=7)
        end_date = datetime.date.today()
        lastseven = sell.objects.filter(
            date__range=[start_date, end_date], delivered=False)
        acc.total = cool_number(acc.total)
        lastsevenbydate = sell.objects.filter(
            date__range=[start_date, end_date], delivered=True)

        lastsevenbydate = lastsevenbydate.values('date').order_by(
            'date').annotate(total_quantity=Sum('quantity'))
        labels7 = []
        data7 = []
        for i in lastsevenbydate:
            labels7.append(i['date'].strftime('%d/%m/%Y'))
            data7.append(i['total_quantity'])

        lastSevenByPrice = sell.objects.filter(
            date__range=[start_date, end_date], delivered=True)

        lastSevenByPrice = lastSevenByPrice.values('date').order_by(
            'date').annotate(total_price=Sum('total_price'))
        labelsp7 = []
        datap7 = []
        for i in lastSevenByPrice:
            labelsp7.append(i['date'].strftime('%d/%m/%Y'))
            datap7.append(i['total_price'])

        return render(request, 'inventory.html', {'account': acc, 'data': contex, 'pending': lastseven, 'labels7': labels7, 'data7': data7, 'labelsp7': labelsp7, 'datap7': datap7})
    return redirect(index)


# category
def category(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            catname = request.POST['category']
            check = cat.objects.filter(name=catname)
            if check.exists() or catname == "":
                print('Not Entering Duplicate')
                return redirect(category)
            else:
                cat.objects.create(name=catname)

            return redirect(category)

        catp = cat.objects.all()

        page = request.GET.get('page', 1)
        paginator = Paginator(catp, 6)
        try:
            all_cat = paginator.page(page)
        except PageNotAnInteger:
            all_cat = paginator.page(1)
        except EmptyPage:
            all_cat = paginator.page(paginator.num_pages)

        return render(request, 'option/category.html', {'cat_name': all_cat})
    else:
        return redirect('index')


def del_category(request, id):
    if request.user.is_authenticated:
        print(request.method)
        cat.objects.filter(id=id).delete()
        return redirect(category)
    return render(request, 'index.html')


def products(request):
    if request.user.is_authenticated:
        prod = product.objects.all()
        if request.method == 'POST':
            prod = prod.filter(title__icontains=request.POST['search'])
        page = request.GET.get('page', 1)
        paginator = Paginator(prod, 6)
        try:
            all_product = paginator.page(page)
        except PageNotAnInteger:
            all_product = paginator.page(1)
        except EmptyPage:
            all_product = paginator.page(paginator.num_pages)

        return render(request, 'option/products.html', {'product': all_product})
    return render(request, 'index.html')


def add_products(request):
    if request.user.is_authenticated:

        if request.method == 'POST':
            title = request.POST['title']
            price = request.POST['price']
            stock = request.POST['stock']
            catname = request.POST['category']
            product.objects.create(
                title=title, price=price, stock=stock, category=catname)
            updateCat = cat.objects.get(name=catname)
            updateCat.count += 1
            updateCat.save()
            return redirect(products)
        else:
            allcat = cat.objects.all()
            return render(request, 'option/add_product.html', {'cat': allcat})

    return render(request, 'index.html')


def sell_product(request, id):
    if request.user.is_authenticated:
        single_product = product.objects.filter(id=id)
        if request.method == 'POST':
            product_id = id
            product_title = single_product[0].title
            category = single_product[0].category
            buyer = request.POST['buyer_name']
            quantity = request.POST['quantity']
            total_price = int(single_product[0].price) * int(quantity)
            sell.objects.create(product_id=product_id, product_title=product_title,
                                buyer=buyer, quantity=quantity, total_price=total_price, category=category)

            updateProduct = product.objects.get(id=id)
            updateProduct.stock -= int(quantity)
            updateProduct.total_sell += int(quantity)
            updateProduct.save()
            acc = accounts.objects.all()[:1].get()
            acc.clearence += total_price
            acc.save()

            return redirect(products)

        else:
            return render(request, 'option/sell_product.html', {'product': single_product[0]})
    else:
        return redirect(index)


def sells(request):
    if request.user.is_authenticated:
        all_sells = sell.objects.all().order_by('-id')
        if request.method == 'POST':
            search = request.POST['search']
            try:
                all_sells = all_sells.filter(id=search)
            except ValueError:
                print("valueError")

        page = request.GET.get('page', 1)
        paginator = Paginator(all_sells, 10)
        try:
            all_sells = paginator.page(page)
        except PageNotAnInteger:
            all_sells = paginator.page(1)
        except EmptyPage:
            all_sells = paginator.page(paginator.num_pages)

        return render(request, 'option/sells.html', {'sells': all_sells})


def deliverd(request, id):
    if request.user.is_authenticated:
        single_product = sell.objects.get(id=id)
        single_product.delivered = True
        single_product.save()
        single_product = sell.objects.get(id=id)
        acc = accounts.objects.all()[:1].get()
        acc.clearence -= single_product.total_price
        acc.total += single_product.total_price
        acc.save()

        return redirect(sells)
    else:
        return redirect(index)


def edit_product(request, id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            title = request.POST['title']
            price = request.POST['price']
            stock = request.POST['stock']
            catname = request.POST['category']
            updateCat = cat.objects.get(
                name=product.objects.filter(id=id)[0].category)
            updateCat.count -= 1
            updateCat.save()

            update_product = product.objects.get(id=id)
            update_product.title = title
            update_product.price = price
            update_product.stock = stock
            update_product.category = catname
            update_product.save()
            updateCat = cat.objects.get(name=catname)
            updateCat.count += 1
            updateCat.save()

            return redirect(products)
        else:
            singleProduct = product.objects.filter(id=id)
            allcat = cat.objects.all()
            return render(request, 'option/edit_product.html', {'product': singleProduct[0], 'cat': allcat})
    else:
        return redirect(index)


def del_product(request, id):
    if request.user.is_authenticated:
        catname = product.objects.filter(id=id)[0].category
        updateCat = cat.objects.get(name=catname)
        updateCat.count -= 1
        updateCat.save()
        print(id)
        product.objects.filter(id=id).delete()
        return redirect(products)

    return render(request, 'index.html')


def reports(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            starting = request.POST['starting_date']
            ending = request.POST['ending_date']
            all_sells = sell.objects.all().order_by(
                '-date').filter(date__range=[starting, ending], delivered=True)
            sells_by_day = sell.objects.all().order_by(
                '-date').filter(date__range=[starting, ending], delivered=True).values('date').annotate(total_price=Sum('total_price'))

            product_by_day = sell.objects.all().order_by(
                '-date').filter(date__range=[starting, ending], delivered=True).values('date').annotate(total_quantity=Sum('quantity'))

            product_quantity_by_day = sell.objects.all().filter(date__range=[starting, ending], delivered=True).values(
                'product_title').annotate(total_quantity=Sum('quantity'))

            category_quantity_by_day = sell.objects.all().filter(date__range=[starting, ending], delivered=True).values(
                'category').annotate(total_quantity=Sum('quantity'))

            return render(request, 'option/reports.html', {'all_sells': all_sells, 'sells_by_day': sells_by_day, 'product_by_day': product_by_day, 'product_quantity_by_day': product_quantity_by_day, 'category_quantity_by_day': category_quantity_by_day})
        return render(request, 'option/reports.html')

    return redirect(index)
