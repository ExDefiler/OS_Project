from socket import *

SERVER = gethostbyname(gethostname())
PORT = 2021
CLIENT_PORT = 2022
BUF_SIZE = 1024

server = socket(AF_INET, SOCK_STREAM)
server.bind((SERVER, PORT))


def start():

    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")

    while True:

        conn, address = server.accept()
        connected = True
        msg_socket = socket(AF_INET, SOCK_STREAM)

        username = conn.recv(BUF_SIZE).decode().split()[1]
        print(f"[NEW CONNECTION] User {username}: {address} connected.")
        conn.send("OK".encode())

        try:
            msg_socket.connect((address[0], CLIENT_PORT))
        except error:
            print("Failed to connect to client's message receiving port.")

        while connected:

            try:
                command = conn.recv(BUF_SIZE).decode()
            except error as err:
                print(err)
                break

            if command:
                command = command.split()

                if len(command) == 1:

                    if command[0] == "DISCONNECT":
                        conn.send("OK".encode())
                        conn.close()
                        msg_socket.close()
                        print(f"[END OF SESSION] User {username} disconnected.")
                        connected = False

                    elif command[0] == "LU":
                        conn.send(f"{username}\n".encode())

                    elif command[0] == "LF":
                        conn.send("Available in the future. Stay tuned!\n".encode())

                    else:
                        conn.send("Violating protocols. Being disconnected from server.".encode())
                        conn.close()
                        msg_socket.close()
                        connected = False

                elif len(command) == 2:

                    if command[0] == "READ":
                        conn.send("OK".encode())

                    elif command[0] == "WRITE":
                        conn.send("OK".encode())

                    elif command[0] == "OVERREAD":
                        conn.send("OK".encode())

                    elif command[0] == "OVERWRITE":
                        conn.send("OK".encode())

                    elif command[0] == "APPEND":
                        conn.send("OK".encode())

                elif len(command) == 3 and command[0] == "APPENDFILE":
                    conn.send("OK".encode())

                elif command[0] == "MESSAGE" and len(command) >= 4:
                    msg_socket.send("Message delivered".encode())
                    conn.send("OK".encode())

                else:
                    conn.send("Violating protocols. Being disconnected from server.".encode())
                    conn.close()
                    msg_socket.close()
                    connected = False

            else:
                print(f"[END OF SESSION] User {username} disconnected.")
                conn.close()
                msg_socket.close()
                connected = False


print("[STARTING] Server is starting...")
start()
