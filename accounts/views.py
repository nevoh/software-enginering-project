
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from Core.models import User
from accounts.forms import EditProfileForm
from listing.models import Listing
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.core.mail import send_mail
from inquiry.models import inquiry
from listing.forms import UpdateForm
import random
import string


def randomString(stringlength=6):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(stringlength))


code = randomString()


def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']
        password2 = request.POST['password2']
        user = User

        context = {
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'email': email,
            'phone': phone,
            'password': password,
        }

        if password == password2:
            if user.objects.filter(username=username).exists():
                messages.error(request, 'Username is already taken')
                return redirect('register')
            else:
                if user.objects.filter(email=email).exists():
                    messages.error(request, 'Email is already used')
                    return redirect('register')
                else:
                    if user.objects.filter(phone=phone).exists():
                        messages.error(request, 'Phone no  is already used')
                        return redirect('register')
                    else:
                        send_mail(
                            'Account Creation Confirmation',
                            'Hi ' + first_name + 'You Confirmation code is: ' + code,
                            'nevogola@gmail.com',
                            [email],
                            fail_silently=False
                        )
                        request.method = 'GET'
                        return render(request, 'accounts/confirmregister.html', context)
        else:
            messages.error(request, 'passwords do not match')
            return redirect('register')
    else:
        return render(request, 'accounts/register.html')


def confirmregister(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']
        confirmcode = request.POST['confirmcode']
        user = User
        context = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'username': username,
            'phone': phone,
            'password': password,
        }
        if code == confirmcode:
            user = user.objects.create_user(
                username=username, password=password, email=email, phone=phone, first_name=first_name, last_name=last_name)
            user.save()
            login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect('index')
        else:
            messages.error(request, 'Invalid Confirmation Code')
            return render(request, 'accounts/confirmregister.html', context)
    else:
        return redirect('register')


def userlogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect('index')
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('login')
    else:
        return render(request, 'accounts/login.html')


@login_required
def userlogout(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, "you are now logged out")
        return redirect('index')


@login_required
def dashboard(request):
    mylistings = Listing.objects.order_by(
        '-list_date').filter(owner=request.user)
    context = {
        'listings': mylistings
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def myinquiries(request):
    myinquiry = inquiry.objects.all().filter(user_id=request.user.id)
    context = {
        'myinquiries': myinquiry
    }
    return render(request, 'accounts/dashboard_myinquiries.html', context)


@login_required
def inquiry1(request):
    myinquiry = inquiry.objects.all().filter(owner_id=request.user.id)
    context = {
        'inquiries': myinquiry
    }
    return render(request, 'accounts/dashboard_inquiries.html', context)


@login_required
def send_reply(request):
    if request.method == "POST":
        email = request.POST['email']
        message = request.POST['message']
        lisiting = request.POST['listing']
        send_mail(
            'Reply from ' + lisiting + ' owner',
            message,
            'nevogola@gmail.com',
            [email],
            fail_silently=False
        )
        messages.success(request, 'Your reply has been sent successfully')
        return redirect('inquiry1')
    else:
        return redirect('dashboard')


def user_profile(request):
    args = {'user': request.user}
    return render(request, 'accounts/user_profile.html', args)


def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect('/accounts/user_profile')
    else:
        form = EditProfileForm(instance=request.user)
        args = {'form': form}
        return render(request, 'accounts/edit_profile.html', args)


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)

        if form.is_valid():
            form.save()
            messages.success(
                request, "Password succesfully changed. Please log in with your new password.")
            return redirect('/accounts/login')
        else:
            messages.error(
                request, 'Please ensure you have entered the correct information')
            return redirect('/accounts/change_password')
    else:
        form = PasswordChangeForm(user=request.user)
        args = {'form': form}
        return render(request, 'accounts/change_password.html', args)


@login_required
def add_favourite(request, id):
    post = get_object_or_404(Listing, id=id)
    if post.favourites.filter(id=request.user.id).exists():
        post.favourites.remove(request.user)
    else:
        post.favourites.add(request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def favourites_list(request):
    new = Listing.objects.order_by(
        '-list_date').filter(favourites=request.user)
    return render(
        request,
        'accounts/favourites.html',
        {'new': new}
    )
