'''
Maksym Sagadin
Sergio Chairez

'''

import socket
import pickle
import sys 

HOST = '127.0.0.1'
BUFFER_SIZE = 1024
PORT = int(sys.argv[1])

menu = '''
Choose a service: 
1 - Get current directory
2 - Change directory
3 - List current directory
4 - Create a new file
q - Quit
'''

def display_request(input):
    print(input)


def main():
    """
    main function that runs the program and calls helper
    functions
    """
    with socket.socket() as client :
        client.connect((HOST, PORT))
        print("Client connected to:", HOST, "port:", PORT)
        mesg = "1"
        client.send(mesg.encode('utf-8'))
        fromServer = client.recv(BUFFER_SIZE).decode('utf-8')
        display_request(fromServer)

        while mesg != 'q':
            # print("Received from server:", fromServer)
            print (menu)
            mesg = input("Enter number to send or q to quit: ")
            client.send(mesg.encode('utf-8'))

            if mesg == '2':
                print(client.recv(BUFFER_SIZE).decode('utf-8'))
                mesg = input("")
                client.sendall(mesg.encode('utf-8'))
                result = client.recv(BUFFER_SIZE).decode('utf-8')

            elif mesg == '3':
                result = client.recv(BUFFER_SIZE).decode('utf-8')
                display_request(result)
                result = client.recv(BUFFER_SIZE)
                result = pickle.loads(result)
                if len(result) == 0:
                    result = "Directory is Empty"
                else:
                    result = "\n".join(result)

            elif mesg == '4':
                print(client.recv(BUFFER_SIZE).decode('utf-8'))
                mesg = input("")
                client.sendall(mesg.encode('utf-8'))
                result = client.recv(BUFFER_SIZE).decode('utf-8')
            else: 
                result = client.recv(BUFFER_SIZE).decode('utf-8')

            display_request(result)
            result = ''  #reset
            

if __name__ == "__main__":
    main()
