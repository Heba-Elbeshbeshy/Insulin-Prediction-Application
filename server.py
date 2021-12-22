import socket
from sys import argv
import threading
import pandas as pd
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split


##CONSTANTS for TCP connection Stream
IP="127.0.0.1"
PORT = 7070 #Port to listen on 
FORMAT = 'utf-8'
number = 0

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
server.bind((IP, PORT))
server.listen()

clients=[]
userNames =[]
answers = []

diabetes_data = pd.read_csv('diabetes.csv')

x=diabetes_data.drop(["Outcome"],axis = 1)

y=diabetes_data['Outcome']

X_train,X_test,y_train,y_test = train_test_split(x,y,test_size=0.2,random_state=42)

classifer = GaussianNB()

fitted_data = classifer.fit(X_train,y_train)
print("Classifier Trained")


def model(client):
    prediction=classifer.predict(np.array(client).reshape(1, -1))
    if prediction[0] == 0:
        return 'You are not a diabtic'
    else:
        return 'You probably a diabtic, consult a doctor ASAP'

#Broadcast fun that sends a messge to all connected devices 
def broadcast(msg, client):
    client.send(msg) # send Decoded msg for any new client

# Handle every induvudual connection to the client
def handle(client):
    while True:
        try:
            msg = client.recv(1024)
            for word in msg.split():
                if word.isdigit():
                    answers[clients.index(client)].append(int(word))
           
            if len(answers[clients.index(client)]) == 6:
                broadcast(msg, client)
                msg = model(answers[clients.index(client)])
                broadcast(msg.encode(FORMAT), client)
            else:
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
        answers.append([])
        print(f"Accept new connection with {str(clientAddress)}")

        #ask for client user name
        client.send("USERNAME".encode(FORMAT))  
        userName = client.recv(1024)

        userNames.append(userName)
        clients.append(client)

        thread = threading.Thread(target=handle , args=(client, ))
        thread.start()
        print("Server Running")

receive(clients) 


