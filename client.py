import socket
import argparse
import threading
import sys

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(message)
            sys.stdout.flush()
        except:
            break

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-join", action="store_true")
    parser.add_argument("-host", type=str, required=True)
    parser.add_argument("-port", type=int, required=True)
    parser.add_argument("-username", type=str, required=True)
    parser.add_argument("-passcode", type=str, required=True)
    args = parser.parse_args()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((args.host, args.port))

    client.send((args.username + '|' + args.passcode).encode('utf-8'))

    response = client.recv(1024).decode('utf-8')
    print(response)
    sys.stdout.flush()

    threading.Thread(target=receive_messages, args=(client,)).start()

    try:
        while True:
            try:
                msg = input()
            except EOFError:
                return
            if not msg:
                continue
            if msg == ":Exit":
                client.send(":Exit".encode('utf-8'))
                break
            client.send(msg.encode('utf-8'))
    except KeyboardInterrupt:
        client.close()


if __name__ == "__main__":
    main()
