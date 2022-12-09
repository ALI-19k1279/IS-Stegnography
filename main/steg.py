import numpy as np
import pandas as pand
import os
import cv2
import rsa
import win32api
from base64 import b64encode, b64decode
import wave
import hashlib
import scipy.ndimage as spi
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from django.conf import settings as django_settings
pw=[]
frame_=[[[]]]
def txt_encode(text,filepath,nameoffile):
    l=len(text)
    i=0
    add=''
    while i<l:
        t=ord(text[i])
        if(t>=32 and t<=64):
            t1=t+48
            t2=t1^170       #170: 10101010
            res = bin(t2)[2:].zfill(8)
            add+="0011"+res
        
        else:
            t1=t-48
            t2=t1^170
            res = bin(t2)[2:].zfill(8)
            add+="0110"+res
        i+=1
    res1=add+"111111111111"
    print("The string after binary conversion appyling all the transformation :- " + (res1))   
    length = len(res1)
    print("Length of binary after conversion:- ",length)
    HM_SK=""
    ZWC={"00":u'\u200C',"01":u'\u202C',"11":u'\u202D',"10":u'\u200E'}  
    file1 = filepath  
    filename=nameoffile
    print(filename)
    file3= open(os.path.join(django_settings.STATIC_ROOT, filename),"w+", encoding="utf-8")
    word=[]
    for line in file1: 
        word+=line.split()
    i=0
    while(i<len(res1)):  
        s=word[int(i/12)]
        j=0
        x=""
        HM_SK=""
        while(j<12):
            x=res1[j+i]+res1[i+j+1]
            HM_SK+=ZWC[x]
            j+=2
        # print(type(s.decode('utf-8')))
        # print(type(HM_SK))
        s1=s.decode('utf-8')+HM_SK
        file3.write(s1)
        file3.write(" ")
        i+=12
    t=int(len(res1)/12)     
    while t<len(word): 
        file3.write(word[t].decode('utf-8'))
        file3.write(" ")
        t+=1
    file3.close()  
    file1.close()
    print("\nStego file has successfully generated")
    
def encode_txt_data(filepath,text1,nameoffile):
    count2=0
    file1 = filepath      #open(filepath,"r")
    for line in file1: 
        print(line)
        for word in line.split():
            count2=count2+1
        
    bt=int(count2)
    
    print("Maximum number of words that can be inserted :- ",int(bt/6))
    l=len(text1)
    if(l<=bt):
        print("\nInputed message can be hidden in the cover file\n")
        txt_encode(text1,filepath,nameoffile)
        file1.close()   
    else:
        print("\nString is too big please reduce string size")
        return 
        
def BinaryToDecimal(binary):
    string = int(binary, 2)
    return string


def decode_txt_data(stego):
    ZWC_reverse={u'\u200C':"00",u'\u202C':"01",u'\u202D':"11",u'\u200E':"10"}
    #
    file4= open(os.path.join(django_settings.STATIC_ROOT, stego),"r", encoding="utf-8")
    temp=''
    for line in file4: 
        for words in line.split():
            T1=words
            binary_extract=""
            for letter in T1:
                if(letter in ZWC_reverse):
                    binary_extract+=ZWC_reverse[letter]
            if binary_extract=="111111111111":
                break
            else:
                temp+=binary_extract
    print("\nEncrypted message presented in code bits:",temp) 
    lengthd = len(temp)
    print("\nLength of encoded bits:- ",lengthd)
    i=0
    a=0
    b=4
    c=4
    d=12
    final=''
    while i<len(temp):
        t3=temp[a:b]
        a+=12
        b+=12
        i+=12
        t4=temp[c:d]
        c+=12
        d+=12
        if(t3=='0110'):
            decimal_data = BinaryToDecimal(t4)
            final+=chr((decimal_data ^ 170) + 48)
        elif(t3=='0011'):
            decimal_data = BinaryToDecimal(t4)
            final+=chr((decimal_data ^ 170) - 48)
    print("\nMessage after decoding from the stego file:- ",final)
    return final
        
    
def msgtobinary(msg):
    if type(msg) == str:
        result= ''.join([ format(ord(i), "08b") for i in msg ])
    
    elif type(msg) == bytes or type(msg) == np.ndarray:
        result= [ format(i, "08b") for i in msg ]
    
    elif type(msg) == int or type(msg) == np.uint8:
        result=format(msg, "08b")

    else:
        raise TypeError("Input type is not supported in this function")
    
    return result


def encode_img_data(image,data,nameoffile): 
    if (len(data) == 0): 
        raise ValueError('Data entered to be encoded is empty')   
    # img_str=image.read()
    # nparr = np.fromstring(img_str, np.uint8)
    img_np = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_UNCHANGED)
    #resized_image = cv2.resize(img_np, (100, 100)) #resize the image as per your requirement
    #cv2.imshow(resized_image,mat)
    no_of_bytes=(img_np.shape[0] * img_np.shape[1] * 3) // 8
    
    print("\t\nMaximum bytes to encode in Image :", no_of_bytes)
    
    if(len(data)>no_of_bytes):
        raise ValueError("Insufficient bytes Error, Need Bigger Image or give Less Data !!")
    
    data +='*^*^*'    
    
    binary_data=msgtobinary(data)
    print("\n")
    print(binary_data)
    length_data=len(binary_data)
    
    print("\nThe Length of Binary data",length_data)
    
    index_data = 0
    
    for i in img_np:
        for pixel in i:
            r, g, b = msgtobinary(pixel)
            if index_data < length_data:
                pixel[0] = int(r[:-1] + binary_data[index_data], 2) 
                index_data += 1
            if index_data < length_data:
                pixel[1] = int(g[:-1] + binary_data[index_data], 2) 
                index_data += 1
            if index_data < length_data:
                pixel[2] = int(b[:-1] + binary_data[index_data], 2) 
                index_data += 1
            if index_data >= length_data:
                break
            #os.path.join(django_settings.STATIC_ROOT, nameoffile)
    cv2.imwrite(os.path.join(django_settings.STATIC_ROOT, nameoffile),img_np)
    print("\nEncoded the data successfully in the Image and the image is successfully saved with name ",nameoffile)
    
def decode_img_data(image):
        img=cv2.imread(os.path.join(django_settings.STATIC_ROOT, image))
        #print(image.content_type)
        #resized_image = cv2.resize(img, (100, 100))  #resize the original image as per your requirement
        #cv2.imshow(resized_image) #display the Steganographed image
        data_binary = ""
        for i in img:
            for pixel in i:
                r, g, b = msgtobinary(pixel) 
                data_binary += r[-1]  
                data_binary += g[-1]  
                data_binary += b[-1]  
                
        total_bytes = [ data_binary[i: i+8] for i in range(0, len(data_binary), 8) ]
        #print(total_bytes)
        decoded_data = ""
        for byte in total_bytes:
            decoded_data += chr(int(byte, 2))
            if decoded_data[-5:] == "*^*^*": 
                print("\n\nThe Encoded data which was hidden in the Image was :--  ",decoded_data[:-5])
                return decoded_data[:-5]

def encode_aud_data(nameoffile,data,stegofile):
    #nameoffile=input("Enter name of the file (with extension) :- ")
    song = wave.open(nameoffile, mode='rb')

    nframes=song.getnframes()
    frames=song.readframes(nframes)
    frame_list=list(frames)
    frame_bytes=bytearray(frame_list)

    #data = input("\nEnter the secret message :- ")

    res = ''.join(format(i, '08b') for i in bytearray(data, encoding ='utf-8'))     
    print("\nThe string after binary conversion :- " + (res))   
    length = len(res)
    print("\nLength of binary after conversion :- ",length)

    data = data + '*^*^*'
    print(data)
    result = []
    for c in data:
        bits = bin(ord(c))[2:].zfill(8)
        result.extend([int(b) for b in bits])

    j = 0
    for i in range(0,len(result),1): 
        res = bin(frame_bytes[j])[2:].zfill(8)
        if res[len(res)-4]== result[i]:
            frame_bytes[j] = (frame_bytes[j] & 253)      #253: 11111101
        else:
            frame_bytes[j] = (frame_bytes[j] & 253) | 2
            frame_bytes[j] = (frame_bytes[j] & 254) | result[i]
        j = j + 1
    
    frame_modified = bytes(frame_bytes)

    #stegofile=input("\nEnter name of the stego file (with extension) :- ")
    with wave.open(os.path.join(django_settings.STATIC_ROOT, stegofile), 'wb') as fd:
        fd.setparams(song.getparams())
        fd.writeframes(frame_modified)
    print("\nEncoded the data successfully in the audio file.")    
    song.close()
    
def decode_aud_data(nameoffile):
    song = wave.open(os.path.join(django_settings.STATIC_ROOT, nameoffile), mode='rb')

    nframes=song.getnframes()
    frames=song.readframes(nframes)
    frame_list=list(frames)
    frame_bytes=bytearray(frame_list)

    extracted = ""
    p=0
    for i in range(len(frame_bytes)):
        if(p==1):
            break
        res = bin(frame_bytes[i])[2:].zfill(8)
        if res[len(res)-2]==0:
            extracted+=res[len(res)-4]
        else:
            extracted+=res[len(res)-1]
    
        all_bytes = [ extracted[i: i+8] for i in range(0, len(extracted), 8) ]
        decoded_data = ""
        for byte in all_bytes:
            decoded_data += chr(int(byte, 2))
            if decoded_data[-5:] == "*^*^*":
                print("The Encoded data was :--",decoded_data[:-5])
                p=1
                return decoded_data[:-5]


def KSA(key):
    key_length = len(key)
    S=list(range(256)) 
    j=0
    for i in range(256):
        j=(j+S[i]+key[i % key_length]) % 256
        S[i],S[j]=S[j],S[i]
    return S

def PRGA(S,n):
    i=0
    j=0
    key=[]
    while n>0:
        n=n-1
        i=(i+1)%256
        j=(j+S[i])%256
        S[i],S[j]=S[j],S[i]
        K=S[(S[i]+S[j])%256]
        key.append(K)
    return key

def preparing_key_array(s):
    return [ord(c) for c in s]

def encryption(plaintext,key):
    #print("Enter the key : ")
    #key=input()
    key=preparing_key_array(key)

    S=KSA(key)

    keystream=np.array(PRGA(S,len(plaintext)))
    plaintext=np.array([ord(i) for i in plaintext])

    cipher=keystream^plaintext
    ctext=''
    for c in cipher:
        ctext=ctext+chr(c)
    return ctext

def decryption(ciphertext,key):
    # print("Enter the key : ")
    # key=input()
    key=preparing_key_array(key)

    S=KSA(key)

    keystream=np.array(PRGA(S,len(ciphertext)))
    ciphertext=np.array([ord(i) for i in ciphertext])

    decoded=keystream^ciphertext
    dtext=''
    for c in decoded:
        dtext=dtext+chr(c)
    return dtext


def extract(frame,key):
    data_binary = ""
    final_decoded_msg = ""
    for i in frame:
        for pixel in i:
            r, g, b = msgtobinary(pixel) 
            data_binary += r[-1]  
            data_binary += g[-1]  
            data_binary += b[-1]  
            total_bytes = [ data_binary[i: i+8] for i in range(0, len(data_binary), 8) ]
            decoded_data = ""
            for byte in total_bytes:
                decoded_data += chr(int(byte, 2))
                if decoded_data[-5:] == "*^*^*": 
                    for i in range(0,len(decoded_data)-5):
                        final_decoded_msg += decoded_data[i]
                    final_decoded_msg = decryption(final_decoded_msg,key)
                    print("\n\nThe Encoded data which was hidden in the Video was :--\n",final_decoded_msg)
                    return final_decoded_msg
                
def embed(frame,data,key):
    #data=input("\nEnter the data to be Encoded in Video :") 
    data=encryption(data,key)
    print("The encrypted data is : ",data)
    if (len(data) == 0): 
        raise ValueError('Data entered to be encoded is empty')

    data +='*^*^*'
    
    binary_data=msgtobinary(data)
    length_data = len(binary_data)
    
    index_data = 0
    
    for i in frame:
        for pixel in i:
            r, g, b = msgtobinary(pixel)
            if index_data < length_data:
                pixel[0] = int(r[:-1] + binary_data[index_data], 2) 
                index_data += 1
            if index_data < length_data:
                pixel[1] = int(g[:-1] + binary_data[index_data], 2) 
                index_data += 1
            if index_data < length_data:
                pixel[2] = int(b[:-1] + binary_data[index_data], 2) 
                index_data += 1
            if index_data >= length_data:
                break
        return frame
                  
def encode_vid_data(vid,data,stegvid,key,n):
    cap=cv2.VideoCapture(vid.name)
    vidcap = cv2.VideoCapture(vid.name)  
    frame_=[[[]]]  
    #fourcc = cv2.VideoWriter_fourcc(*'XVID')
    frame_width = int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    size = (frame_width, frame_height)
    out = cv2.VideoWriter(os.path.join(django_settings.STATIC_ROOT, stegvid),cv2.VideoWriter_fourcc(*"mp4v"), 25.0, size)
    max_frame=0;
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == False:
            break
        max_frame+=1
    cap.release()
    #win32api.MessageBox(0, 'hello', 'title', 0x00001000) 
    win32api.MessageBox(0,f'Total number of Frame in selected Video : {max_frame}',"Info Alert",0x00001000)
    #print("Enter the frame number where you want to embed data : ")
    #n=int(input())
    frame_number = 0
    while(vidcap.isOpened()):
        frame_number += 1
        ret, frame = vidcap.read()
        if ret == False:
            print(ret)
            break
        if frame_number == int(n):
            print(n)    
            change_frame_with = embed(frame,data,key)
            frame_1 = change_frame_with
            frame = change_frame_with
        print(frame)
        out.write(frame)
    
    print("\nEncoded the data successfully in the video file.")
    frame_=frame_1
    # print(frame_)

def decode_vid_data(filename,n,key):
    cap = cv2.VideoCapture(os.path.join(django_settings.STATIC_ROOT, filename))
    max_frame=0;
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == False:
            break
        max_frame+=1
    # print("Total number of Frame in selected Video :",max_frame)
    # print("Enter the secret frame number from where you want to extract data")
    # n=int(input())
    vidcap = cv2.VideoCapture(os.path.join(django_settings.STATIC_ROOT, filename))
    frame_number = 0
    while(vidcap.isOpened()):
        frame_number += 1
        ret, frame = vidcap.read()
        if ret == False:
            break
        if frame_number == n:
            extract(frame_,key)
            return