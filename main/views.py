from django.shortcuts import render,redirect
from .forms import *
from django.contrib.auth.decorators import *
from django.contrib.auth import login,logout,authenticate
# Create your views here.

@login_required(login_url="/login")
def home(request):
    return render(request,'main/home.html')

@login_required(login_url="/login")
def steg(request):
    return render(request,'main/textSteg.html')

def sign_up(request):
    if request.method=='POST':
        form=RegisterForm(request.POST)
        if form.is_valid():
            user=form.save()
            login(request,user)
            return redirect('/home')
            
    else:
        form=RegisterForm()
        
    return render(request,'registration/sign_up.html',{"form":form})

def encode(request):
    if request.method=='POST':
        form=StegForm(request.POST)
        if form.is_valid():
            steg=form.save(commit=False)
            steg.user=request.user
            steg.save()
            #login(request,user)
            return redirect('/home')
            
    else:
        form=StegForm()
        
    return render(request,'main/textSteg.html',{"form":form})