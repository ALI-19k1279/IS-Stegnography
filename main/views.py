from django.shortcuts import render,redirect
from .forms import *
from django.contrib.auth.decorators import *
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate
from django.shortcuts import render
from .steg import *
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from rest_framework.parsers import MultiPartParser
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
            print("hellllooo")
            file=request.FILES['file_to_encode']
            key=form.cleaned_data["key"]
            print(file)
            print(key)
            encode_txt_data(file,form.cleaned_data["hidden_message"],key,form.cleaned_data["filename"])
            #decode_txt_data(form.cleaned_data["filename"],key)
            #steg.save()
            return redirect('/home')
            
    else:
        #print(request)
        print("helos")
        form=StegForm()
        
    return render(request,'main/textSteg.html',{"form":form})

def decode(request):
    if request.method=='POST':
        form=StegDecodeForm(request.POST)
        if form.is_valid():
            steg=form.save(commit=False)
            steg.user=request.user
            print("hellllooo")
            #file=request.FILES['file_to_encode']
            key=form.cleaned_data["key"]
            #print(file)
            print(key)
            print(form.fields.items)
            #encode_txt_data(file,form.cleaned_data["hidden_message"],key,form.cleaned_data["filename"])
            message=decode_txt_data(form.cleaned_data["filename"],key)
            print(message)
            #request["message"]=message
            messages.success(request, message)
            #steg.save()
            
            
    else:
        #print(request)
        print("helos")
        form=StegDecodeForm()
        
    return render(request,'main/decode.html',{"form":form})

class HandleFileUpload(APIView):
    parser_classes = [MultiPartParser]
    def post(self , request):
        try:
            data = request.data

            serializer = FileListSerializer(data = data)
        
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status' : 200,
                    'message' : 'files uploaded successfully',
                    'data' : serializer.data
                })
            
            return Response({
                'status' : 400,
                'message' : 'somethign went wrong',
                'data'  : serializer.errors
            })
        except Exception as e:
            print(e)