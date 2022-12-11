from django.shortcuts import render,redirect
from .forms import *
from django.contrib.auth.decorators import *
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate
from django.shortcuts import render
from .steg import *
import rsa
from urllib3 import encode_multipart_formdata
from rest_framework.decorators import parser_classes
from .models import Steg
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from rest_framework.parsers import MultiPartParser
from Crypto.Cipher import PKCS1_OAEP
import base64
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA512, SHA384, SHA256, SHA, MD5
from Crypto import Random
from base64 import b64encode, b64decode
from base64 import b64encode, b64decode
import hashlib
from Cryptodome.Cipher import AES
import os
from Cryptodome.Random import get_random_bytes
import uuid
CRITICAL = 50
SUCCESS	=25
def encrypt(plain_text, password):
    # generate a random salt
    salt = get_random_bytes(AES.block_size)

    # use the Scrypt KDF to get a private key from the password
    private_key = hashlib.scrypt(
        password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)

    # create cipher config
    cipher_config = AES.new(private_key, AES.MODE_GCM)

    # return a dictionary with the encrypted text
    cipher_text, tag = cipher_config.encrypt_and_digest(bytes(plain_text, 'utf-8'))
    return {
        'cipher_text': b64encode(cipher_text).decode('utf-8'),
        'salt': b64encode(salt).decode('utf-8'),
        'nonce': b64encode(cipher_config.nonce).decode('utf-8'),
        'tag': b64encode(tag).decode('utf-8')
    }
    
def decrypt(enc_dict, password):
    # decode the dictionary entries from base64
    salt = b64decode(enc_dict['salt'])
    cipher_text = b64decode(enc_dict['cipher_text'])
    nonce = b64decode(enc_dict['nonce'])
    tag = b64decode(enc_dict['tag'])
    # generate the private key from the password and salt
    private_key = hashlib.scrypt(
        password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)

    # create the cipher config
    cipher = AES.new(private_key, AES.MODE_GCM, nonce=nonce)
    
    decrypted = cipher.decrypt_and_verify(cipher_text, tag)
    print(decrypted)
    return decrypted


@login_required(login_url="/login")
def home(request):
    print(request.user)
    data=Steg.objects.filter(user=request.user)
    return render(request,'main/home.html',{"data":data})

@login_required(login_url="/login")
def deleteRec(request,filename,_id):
    if(request.method=="POST"):
        if filename and _id:
            record=Steg.objects.filter(filename=filename).first()
            if record and record.user==request.user:
                #os.remove(os.path.join(django_settings.STATIC_ROOT, record.filename))
                record.delete()
                messages.add_message(request,SUCCESS,"Deleted successfully");
            else:
                messages.add_message(request,CRITICAL,"Deletion failed");
    data=Steg.objects.filter(user=request.user)
    return render(request,'main/home.html',{"data":data})

@login_required(login_url="/login")
def steg(request):
    return render(request,'main/Steg.html')

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

def encrypt_private_key(a_message, private_key):
    encryptor = PKCS1_OAEP.new(private_key)
    encrypted_msg = encryptor.encrypt(a_message)
    print(encrypted_msg)
    encoded_encrypted_msg = base64.b64encode(encrypted_msg)
    print(encoded_encrypted_msg)
    return encoded_encrypted_msg

@login_required(login_url="/login")
def encode(request):
    if request.method=='POST':
        form=StegForm(request.POST)
        file={}
        if form.is_valid():
            steg=form.save(commit=False)
            steg.user=request.user
            print("hellllooo")
            filedata=request.FILES['file_to_encode']
            user_key=form.cleaned_data["user_key"]
            user_message=request.POST["message"]
            print(request.POST['stegType'])
            uniq_filename='%s%s' % (form.cleaned_data["filename"],uuid.uuid4())
            enc_dict=encrypt(uniq_filename,user_key)
            steg.user_key=hashlib.sha256(user_key.encode()).digest()
            steg.generated_key=enc_dict.get('cipher_text')
            steg.salt=enc_dict.get('salt')
            steg.nonce=enc_dict.get('nonce')
            steg.tag=enc_dict.get('tag')
            if request.POST['stegType']=="image":
                print(filedata.content_type.split('/')[1])
                uniq_filename=uniq_filename+'.'+filedata.content_type.split('/')[1]
                steg.filename=uniq_filename
                print(uniq_filename)
                encode_img_data(filedata,request.POST["message"],uniq_filename)
            elif request.POST['stegType']=="text":
                print(user_message)
                uniq_filename=uniq_filename+'.'+filedata.content_type.split('/')[1]
                steg.filename=uniq_filename
                encode_txt_data(filedata,request.POST["message"],uniq_filename)
            elif request.POST['stegType']=="audio":
                print(user_message)
                uniq_filename=uniq_filename+'.'+filedata.content_type.split('/')[1]
                steg.filename=uniq_filename
                encode_aud_data(filedata,request.POST["message"],uniq_filename)
            elif request.POST['stegType']=="video":
                frame=request.POST['frame']
                print(user_message)
                uniq_filename=uniq_filename+'.'+filedata.content_type.split('/')[1]
                steg.filename=uniq_filename
                encode_vid_data(filedata,request.POST["message"],uniq_filename,user_key,frame)
            steg.save()
            return redirect('/home')
            
    else:
        print("helos")
        form=StegForm()
        
    return render(request,'main/Steg.html',{"form":form})

@login_required(login_url="/login")
def decode(request):
    message=""
    if request.method=='POST':
        form=StegDecodeForm(request.POST)
        enc_dict={}
        
        if form.is_valid():
            steg=form.save(commit=False)
            steg.user=request.user
            print("hellllooo")
            keyInput=form.cleaned_data["user_key"]
            obj=Steg.objects.get(filename=form.cleaned_data["filename"])
            enc_dict['cipher_text']=obj.generated_key
            enc_dict['salt']=obj.salt
            enc_dict['nonce']=obj.nonce
            enc_dict['tag']=obj.tag
            print(obj.user_key)
            try:
                result=decrypt(enc_dict,keyInput)
            except ValueError:
                result="failed"
            if result!="failed":
                if result.decode()==form.cleaned_data["filename"].split('.')[0]:
                        if request.POST['stegType']=="image":
                            print(form.cleaned_data["filename"])
                            message=decode_img_data(form.cleaned_data["filename"])
                        elif request.POST['stegType']=="text":
                            message=decode_txt_data(form.cleaned_data["filename"])
                        elif request.POST['stegType']=="audio":
                            message=decode_aud_data(form.cleaned_data["filename"])
                        elif request.POST['stegType']=="video":
                            frame=request.POST['frame']
                            message=decode_vid_data(form.cleaned_data["filename"],frame,keyInput)
                        print("wjasa")
                        print(message)
                        messages.success(request, message)
                else:
                    print("hhh")
                    result="failed22"
            else:
                win32api.MessageBox(0,"Authentication Failed!!!","** Alert **",0x00001000)
                messages.error(request,"")
    else:
        print("helos")
        form=StegDecodeForm()
    return render(request,'main/decode.html',{"form":form})




def download(request , uid):
    return render(request , 'download.html' , context = {'uid' : uid})



