import socket
import threading
import sys

clients = []
subscribers = {}

def handle_client(client_socket, client_address, role, topic):
    global clients, subscribers
    if role == "SUBSCRIBER":
        if topic not in subscribers:
            subscribers[topic] = []
        subscribers[topic].append(client_socket)

    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            if message.strip().lower() == "terminate":
                print(f"{client_address} terminated connection.")
                break
            print(f"Received from {client_address} on topic {topic}: {message}")
            if role == "PUBLISHER":
                if topic in subscribers:
                    for subscriber in subscribers[topic]:
                        if subscriber != client_socket:
                            subscriber.sendall(f"Publisher {client_address} on {topic}: {message}".encode('utf-8'))
    finally:
        if role == "SUBSCRIBER":
            subscribers[topic].remove(client_socket)
            if not subscribers[topic]:
                del subscribers[topic]
        clients.remove((client_socket, client_address))
        client_socket.close()

def start_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    print(f"Server on port {port}")

    while True:
        client_socket, client_address = server_socket.accept()
        role_topic = client_socket.recv(1024).decode('utf-8').split()
        role = role_topic[0].upper()
        topic = role_topic[1].upper()
        print(f"Connection from {client_address} as {role} on topic {topic}")
        clients.append((client_socket, client_address))
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address, role, topic))
        client_thread.start()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    start_server(port)
