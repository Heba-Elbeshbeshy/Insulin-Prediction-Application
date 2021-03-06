import socket
import threading
import tkinter
from tkinter.constants import INSERT, S
import tkinter.scrolledtext
from tkinter import Tk, simpledialog


# HEADER_LEN =10
IP="127.0.0.1"
PORT = 7070 #Port to listen on 
FORMAT = 'utf-8'

## class for client
class Client:
    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.connect((ip, port))

        self.NUM_Q = 0
        ## BOT QUESTIONS
        self.Question = ["Please Enter YOUR AGE:", "Please Enter YOUR Glucose Level:", "Please Enter YOUR BloodPressure:", "Please Enter YOUR Insulin Level:", "Please Enter YOUR BMI:", "Please Enter YOUR Pregnancies time:", "", ""]

        # Starting Window
        msg = tkinter.Tk()
        msg.withdraw()
        self.userName = simpledialog.askstring("UserName", "Please enter your username", parent=msg)
        
        if type(self.userName) != type(None): # when user enter his USERNAME
            self.gui_done = False ## till build all the UI
            self.running = True
            #thread to build the GUI
            gui_thread = threading.Thread(target=self.gui_loop)
            #thread to handle server connections
            receive_thread = threading.Thread(target=self.receive)

            gui_thread.start()
            receive_thread.start()
        else: # IF user didn't enter his USERNAME
            print("Please Enter Your UserName Then Press Ok!")
            self.sock.close()

## Function to buld GUI by Tkinter Library
    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.title("Medical-ChatBot") #title
        self.win.configure(bg="lightgray")

        self.chat_label = tkinter.Label(self.win,text="Chat:", bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area= tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.insert(INSERT, self.Question[self.NUM_Q]+ '\n')
        self.text_area.config(state='disabled')
        

        self.msg_label = tkinter.Label(self.win,text="Message:", bg="lightgray")
        self.msg_label.config(font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area= tkinter.Text(self.win,height=3)
        self.input_area.pack(padx=20, pady=5)
        
        self.sendButton = tkinter.Button(self.win, text=" Send ", command=self.write)
        self.sendButton.config(font=("Arial", 12))
        self.sendButton.pack(side= tkinter.RIGHT, padx=20, pady=5)

        ##GUI IS DOOONEE
        self.gui_done = True
        self.win.protocol("WM_DELETE_WINDOW", self.stop)
        self.win.mainloop()

    ## get the text and send it to the server
    def write(self):
        msg = f"{self.userName}: {self.input_area.get('1.0','end')}"
        self.sock.send(msg.encode(FORMAT))
        self.input_area.delete('1.0','end')        

    def stop(self):
        self.win.destroy()
        self.sock.close()
        exit(0)

    def receive(self):
        while self.running :
            try:
                
                msg = self.sock.recv(1024).decode(FORMAT)
                if msg == 'USERNAME':
                    self.sock.send(self.userName.encode(FORMAT)) ## Take user name 
                    
                elif msg !='': # chek if the user send a valid msg
                    if self.gui_done:
                        self.NUM_Q +=1
                        if self.NUM_Q == len(self.Question) - 1:
                            self.Update_GUI(msg)
                        elif self.NUM_Q < len(self.Question) - 1:
                            self.Update_GUI(msg)
                else: # if user is timedout the connection is closed
                    msg = 'DISCONNECTED'
                    print('connection is closed')
                    self.sock.send(msg.encode(FORMAT))
                    self.sock.close()
                    self.win.destroy()
                    exit(0)
            except ConnectionAbortedError:
                break
            except:
                print("error")
                self.sock.close()
                exit(0)
                break

    def Update_GUI(self, msg): # update the sent msg to the chat of ui 
        self.text_area.config(state='normal')
        self.text_area.insert('end', msg, "center",  '\n' + self.Question[self.NUM_Q] + '\n')
        self.text_area.yview('end')
        self.text_area.config(state='disabled')    

client = Client(IP, PORT)
