from socket import *

HOST = '127.0.0.1'
PORT = 2021
BUF_SIZE = 1024
CONNECTED_USERS = []

with socket(AF_INET, SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    while True:
        print("Waiting for a connection...")
        conn, address = s.accept()
        username = conn.recv(BUF_SIZE).decode().split()[1]
        print(f"Accepted connection request from {username}: {address}.")
        conn.send("OK".encode())

        while True:
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
                        break

                    elif command[0] == "LU":
                        conn.send(f"{username}\n".encode())

                    elif command[0] == "LF":
                        conn.send("Available in the future. Stay tuned!\n".encode())

                    else:
                        conn.send("Violating protocols. Being disconnected from server.".encode())
                        conn.close()
                        break

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
                    conn.send("OK".encode())

                else:
                    conn.send("Violating protocols. Being disconnected from server.".encode())
                    conn.close()
                    break

            else:
                print("The client finished sending. Closing the connection.")
                break
