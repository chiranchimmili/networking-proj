import socket
import argparse
import threading
import sys
import datetime

clients = {}

def process_message(msg):
    if msg == ":)":
        return "[feeling happy]"
    elif msg == ":(":
        return "[feeling sad]"
    elif msg == ":mytime":
        return datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")
    elif msg == ":+1hr":
        one_hour_later = datetime.datetime.now() + datetime.timedelta(hours=1)
        return one_hour_later.strftime("%a %b %d %H:%M:%S %Y")
    else:
        return msg

def broadcast_message(sender_socket, message):
    for client, _ in clients.items():
        if client != sender_socket:
            client.send(message.encode('utf-8'))

def handle_client(client_socket, addr, password):
    data = client_socket.recv(1024).decode('utf-8')
    username, client_pass = data.split('|', 1)

    if client_pass != password:
        client_socket.send("Incorrect passcode".encode('utf-8'))
        client_socket.close()
        return

    print(f"{username} joined the chatroom")
    sys.stdout.flush()
    clients[client_socket] = username
    client_socket.send(f"Connected to {addr[0]} on port {client_socket.getsockname()[1]}".encode('utf-8'))

    broadcast_message(client_socket, f"{username} joined the chatroom")

    try:
        while True:
            msg = client_socket.recv(1024).decode('utf-8')
            if msg == ":Exit":
                print(f"{username} left the chatroom")
                sys.stdout.flush()
                broadcast_message(client_socket, f"{username} left the chatroom")
                break  
                
            msg = process_message(msg)

            formatted_msg = f"{username}: {msg}"
            print(formatted_msg)
            sys.stdout.flush()
            broadcast_message(client_socket, formatted_msg) 

    except:
        pass

    del clients[client_socket]
    client_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-start", action="store_true")
    parser.add_argument("-port", type=int, required=True)
    parser.add_argument("-passcode", type=str, required=True)
    args = parser.parse_args()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', args.port))
    server.listen(5)
    print(f"Server started on port {args.port}. Accepting connections")
    sys.stdout.flush()

    while True:
        client_sock, addr = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_sock, addr, args.passcode))
        client_thread.start()
