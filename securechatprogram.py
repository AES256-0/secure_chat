import socket,sys
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import argparse

parser=argparse.ArgumentParser(description="***help page for secure chat***")
parser.add_argument("--option",type=str,help="--option client/server/keys")
parser.add_argument("--ip",type=str,help="--ip 192.168.0.1")
parser.add_argument("--port",type=int,help="--port 80")

args=parser.parse_args()




def generate_new_key():
    print("***WELCOME GENERATING YOUR KEYS***")
    password=input("enter the password:").encode()
    print("***PLEASE WAIT***\n***key is in the file:key_file***")
    salt=os.urandom(16)
    kdf=PBKDF2HMAC(algorithm=hashes.SHA256(),salt=salt,iterations=1000000,backend=default_backend(),length=32)
    print("her")
    key=base64.urlsafe_b64encode(kdf.derive(password))
    fd=open("key_file","wb")
    fd.write(key)
    fd.close()


def encrypt_data(key):
    data=input(" "*70 + "Enter the data:").encode()
    f=Fernet(key)
    encrypted_data=f.encrypt(data)
    return encrypted_data

def decrypt_data(key,data):
    d=Fernet(key)
    decrypted_data=d.decrypt(data)
    return decrypted_data

def send_data(sock,key):
    data=encrypt_data(key)
    sock.send(data)
 
def recv_data(sock,key):
     data=sock.recv(1024)
     data=decrypt_data(key,data)
     print("\nRecv:"+str(data))


def client_function(ip,port):
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    try:
        sock.connect((ip,port))
    except:
        print("***Error,Cant connect to the device***")
        sys.exit(1)    
    fd=open("key_file","rb")
    key=fd.read()
    while True:
        ret=os.fork()
        if ret==0:
            send_data(sock,key)
        else:
            recv_data(sock,key)
    sock.close()   


def server_function():
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    sock.bind(("127.0.0.1",8090))
    print("***listening***")
    sock.listen(5)
    while True:
        client_sock,addr=sock.accept()
        print("server connected to:"+str(addr))
        fd=open("key_file","rb")
        key=fd.read()
        while True:
            ret=os.fork()
            if  ret==0:
                recv_data(client_sock,key)
            else:    
                send_data(client_sock,key)
        client_sock.close()
    sock.close() 



if __name__=="__main__":
    if args.option=="client":
        client_function(args.ip,args.port)
    elif args.option=="keys":
        generate_new_key()
    elif args.option=="server":
        server_function()
    else:
        print("*Error*")
