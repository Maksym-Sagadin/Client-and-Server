'''
Maksym Sagadin
Sergio Chairez

'''

import socket
import threading
import os
import pickle
import sys


HOST = "127.0.0.1"
PORT = 5551
BUFFER_SIZE = 1024


def validate_cmd_arg():
    """
    validates that the argument passed in via the terminal
    is an integer and returns the amount of ports to designate later on
    """
    try:
        if (1 <= int(sys.argv[1]) < 5):
            return int(sys.argv[1])
        elif (int(sys.argv[1]) > 4 or int(sys.argv[1]) < 1):
            print("Number of clients < 5 please.\nPlease try again. ")
            sys.exit(1)
        # else:
        #     raise SystemExit("Usage: server.py num_of_clients")
    except IndexError:
        raise SystemExit("Usage: server.py num_of_clients")
    except ValueError:
        raise SystemExit("Usage: server.py num_of_clients")


def get_cwd():
    return os.getcwd()

def get_cwd_and_send_mesg(conn):
    """
    gets the current working directory and sends
    a message to client 
    """
    mesg = f"Current Directory: {get_cwd()}"
    conn.sendall(mesg.encode('utf-8'))


def cd_dir_and_send_mesg(conn):
    """
    change directory and send a message to client
    """
    mesg = f"Enter a path, starting from current directory: {get_cwd()}"
    conn.sendall(mesg.encode('utf-8'))
    path = conn.recv(1024).decode('utf-8')
    try:
        os.chdir(path)
        mesg = f"Success: client is at new directory,\nNew directory is {get_cwd()}"
    except:
        mesg = "Fail: new directory is not valid"
    finally:
        conn.sendall(mesg.encode('utf-8'))
        

def ls_current_and_send_mesg(conn):
    """
    list current directory and send message to client
    """
    mesg = f"Directories and files under: {get_cwd()}"
    conn.sendall(mesg.encode('utf-8'))
    data = os.listdir()
    mesgL = pickle.dumps(data)
    conn.sendall(mesgL)

def new_file_and_send_mesg(conn):
    """
    touches new file and sends the message to client
    """
    mesg = "What would you like to name the new file?"
    conn.sendall(mesg.encode('utf-8'))
    filename = conn.recv(BUFFER_SIZE).decode('utf-8')
    if filename in os.listdir():
        mesg = "Fail: file already exists"
    else:
        if sys.platform in ('darwin','linux'):
            os.system(f"touch {filename}")
        elif sys.platform == 'win32':
            os.system(f"echo > {filename}")
        mesg = f"Success: file {filename} is created and located in: {get_cwd()}"
    conn.sendall(mesg.encode('utf-8'))



# incoming client thread request
def new_client_thread_request(conn, addr):
    """
    create a new client thread to process the menu request items
    available on the server instance
    """
    while True:
        fromClient = conn.recv(BUFFER_SIZE).decode('utf-8')
        # if not fromClient: break
        if fromClient:
            if fromClient == 'q':
                conn.close()
                break
     
            elif fromClient in request_types:
                request_types[fromClient](conn)
            else:
                mesg = f"{fromClient}, is not a valid option, enter a valid choice"
                conn.sendall(mesg.encode('utf-8'))



def create_socket(port):
    """
    creates new socket instance and binds to one of the PORTS
    available given the argument passed in starting at PORT=5551
    """
    try:
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, port))
        print("Listening at port:", port)
        s.listen(4)
        return s

    except socket.error as e:
        print("Bind failed. Error", e)
        s.close()
        sys.exit(1)


def socket_thread_request(s):
    """
    creates and starts threads for each socket so that they can run
    and clients can connect at the same time
    """
    with s:
        while True:
            try:
                s.settimeout(60)
                # s.setblocking(False)
                conn, addr = s.accept()
                s.settimeout(None)  # resetting since connected?
                threading.Thread(None, target=new_client_thread_request, args=(conn, addr)).start()
                
            except socket.timeout as e:
                print(e)
                break

            except Exception as e:
                print("Other exception", e, "occurred")
                break


def main():
    """
    main function that runs the program and calls helper
    functions
    """
    max_connections = validate_cmd_arg()
    socket_list = []
    for port in range(PORT, PORT + max_connections):
        socket_list.append(create_socket(port))

    for s in socket_list:
        try:
            threading.Thread(None, socket_thread_request, args=(s,)).start()

        except Exception as e:
            print("Other exception ", e, "occurred")
            break
         

if __name__ == "__main__":
    request_types = {
        '1': get_cwd_and_send_mesg,
        '2': cd_dir_and_send_mesg,
        '3': ls_current_and_send_mesg,
        '4': new_file_and_send_mesg,
    }
    main()

