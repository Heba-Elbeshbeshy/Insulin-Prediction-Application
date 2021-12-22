import socket
from sys import argv
import threading

##CONSTANTS for TCP connection Stream
# IP = socket.gethostbyname(socket.gethostname())
IP="127.0.0.1"
PORT = 7070 #Port to listen on 
FORMAT = 'utf-8'

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
server.bind((IP, PORT))
server.listen()

clients=[]
userNames =[]

#Broadcast fun that sends a messge to all connected devices 
def broadcast(msg, client):
    client.send(msg) # send Decoded msg for any new client

# Handle every induvudual connection to the client
def handle(client):
    while True:
        try:
            msg = client.recv(1024)
            print(f"{userNames[clients.index(client)]} says {msg}")
            broadcast(msg, client)
        except: ## if we get error
            index = clients.index(client)
            clients.remove(client)
            client.close() # close the connection with these dropped client
            userName= userNames[index]
            userNames.remove(userName)
            break 
            

#Receive Listen func and accept any new client 
def receive(clients):
    while True:  ## always listen for any new connection Request
        # accept the connection an have a new client 
        client , clientAddress = server.accept()  # accept func return client socket and address of these client
        print(f"Accept new connection with {str(clientAddress)}")
        #ask for client user name
        client.send("USERNAME".encode(FORMAT))  
        userName = client.recv(1024)
        userNames.append(userName)
        clients.append(client)
        print(f"Username is {userName}")
       
        client.send("connected to the server".encode(FORMAT))
        thread = threading.Thread(target=handle , args=(client, ))
        thread.start()
        print("Server Running")

receive(clients) 


