from django.shortcuts import render,redirect
from .forms import *
from django.contrib.auth.decorators import *
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate
from django.shortcuts import render
from .steg import *
import rsa
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
# Create your views here.
from base64 import b64encode, b64decode
import hashlib
from Cryptodome.Cipher import AES
import os
from Cryptodome.Random import get_random_bytes
# import scrypt, os, binascii

# def encrypt_AES_GCM(msg, password):
#     kdfSalt = os.urandom(16)
#     secretKey = scrypt.hash(password, kdfSalt, N=16384, r=8, p=1, buflen=32)
#     aesCipher = AES.new(secretKey, AES.MODE_GCM)
#     ciphertext, authTag = aesCipher.encrypt_and_digest(msg)
#     return (kdfSalt, ciphertext, aesCipher.nonce, authTag)

# def decrypt_AES_GCM(encryptedMsg, password):
#     (kdfSalt, ciphertext, nonce, authTag) = encryptedMsg
#     secretKey = scrypt.hash(password, kdfSalt, N=16384, r=8, p=1, buflen=32)
#     aesCipher = AES.new(secretKey, AES.MODE_GCM, nonce)
#     plaintext = aesCipher.decrypt_and_verify(ciphertext, authTag)
#   return plaintext

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

    # decrypt the cipher text
    decrypted = cipher.decrypt_and_verify(cipher_text, tag)

    return decrypted


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
def encrypt_private_key(a_message, private_key):
    encryptor = PKCS1_OAEP.new(private_key)
    encrypted_msg = encryptor.encrypt(a_message)
    print(encrypted_msg)
    encoded_encrypted_msg = base64.b64encode(encrypted_msg)
    print(encoded_encrypted_msg)
    return encoded_encrypted_msg

def encode(request):
    if request.method=='POST':
        form=StegForm(request.POST)
        if form.is_valid():
            steg=form.save(commit=False)
            steg.user=request.user
            print("hellllooo")
            file=request.FILES['file_to_encode']
            user_key=form.cleaned_data["user_key"]
            user_message=request.POST["message"]
            steg.filename=form.cleaned_data["filename"]
            print(user_key)
            print(user_message)
            #print(filename)
            print(request.COOKIES['csrftoken'])
            #print(request.POST["h"])
            enc_dict=encrypt(request.COOKIES['csrftoken'],user_key)
            print(type(enc_dict))
            # publicKey, privateKey = rsa.newkeys(512)
            # real_pw=rsa.encrypt(key.encode(),publicKey)
            # signature = rsa.sign(key.encode(), privateKey, 'SHA-1')
            # steg.hidden_message=signature
            # print(type(publicKey))
            # steg.key=publicKey
            # steg.shareLink=real_pw
            steg.user_key=hashlib.sha256(user_key.encode()).digest()
            steg.generated_key=enc_dict.get('cipher_text')
            steg.salt=enc_dict.get('salt')
            steg.nonce=enc_dict.get('nonce')
            steg.tag=enc_dict.get('tag')
            encode_txt_data(file,request.POST["message"],form.cleaned_data["filename"])
            steg.save()
            return redirect('/home')
            
    else:
        print("helos")
        form=StegForm()
        
    return render(request,'main/textSteg.html',{"form":form})

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
            print(request.COOKIES['csrftoken'])
            print(decrypt(enc_dict,keyInput))
            #if(hashlib.sha256(keyInput.encode())==decrypt(enc_dict,keyInput)):
            if(decrypt(enc_dict,keyInput).decode()==request.COOKIES['csrftoken']):
                message=decode_txt_data(form.cleaned_data["filename"])
                print(message)
                messages.success(request, message)
            else:
                messages.error(request,"key not authorized")
    else:
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
            
