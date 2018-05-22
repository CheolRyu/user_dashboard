# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from .models import *
import bcrypt
import time
import datetime

#landing page
def index(request):
    if 'id' in request.session:
        return redirect("/show/user/" + request.session['id'])
    else:
        return render(request, 'dash_app/index.html')
#signin 
def signin(request):
    if 'id' in request.session:
        return redirect("/show/user/" + request.session['id'])
    else:
        return render(request, 'dash_app/login.html')

def login(request):

    if 'id' in request.session:
        return redirect("/show/user/" + request.session['id'])
    else:
        check = User.objects.login_validation(request.POST)
        print check
        if check[0] == True:
            for tag, error in check[1].iteritems():
                messages.error(request, error, extra_tags=tag)
                return redirect('/signin')
        else:
            user_id = check[1]
            request.session['id'] = str(user_id)
            return redirect("/show/user/" + request.session['id'])

def register(request):
    if 'id' in request.session:
        return redirect("/show/user/" + request.session['id'])
    else:
        return render(request, 'dash_app/register.html')

def registration(request):
    if request.method == "POST":
        if 'id' in request.session:
            return redirect('/show/user/' + request.session['id'])
        else:
            check = User.objects.regi_validation(request.POST)
            print check

            if check[0] == True:
                for tag, error in check[1].iteritems():
                    messages.error(request, error, extra_tags=tag)
                    return redirect('/register')
            else:
                user_id = check[1]
                request.session['id'] = str(user_id)
                return redirect("/show/user/" + request.session['id'])
    else:
        messages.error(request, "Oops, something went wrong.")
        return redirect('/register')
def wall(request, user_id):
    if 'id' not in request.session:
        return redirect('/signin')
    else:
        errors= {}
        user_info = User.objects.get(id=user_id)
        try:
            message_query = Message.objects.filter(receiver=user_id).order_by("-created_at")
            comment_query = Comment.objects.all()
        except:
            errors['msgs'] = 'No posts to display yet'
        if 'msgs' in errors or 'comments' in errors:
            for tag, error in errors.iteritems():
                messages.error(request, error, extra_tags=tag)
                context = {
                'user': user_info,
            }
            return render(request, 'dash_app/show.html', context)
        else:
            context = {
                'user': user_info,
                'msgs': message_query,
                'comments': comment_query
            }
            return render(request, 'dash_app/show.html', context)

def process_message(request,user_id):
    if 'id' not in request.session:
        return redirect('/signin')
    else:
        if request.method == 'POST':
            entry = Message.objects.message_validation(request.POST, user_id, request.session['id'])

            if entry[0] == True:
                for tag, error in check[1].iteritems():
                    messages.error(request, error, extra_tags=tag)
                    return redirect('/show/user/' + user_id)
            else:
                return redirect("/show/user/" + user_id)
        else:
            messages.error(request, "Oops, something went wrong.")
            return redirect('/show/user/' + user_id)

# Create your views here.
