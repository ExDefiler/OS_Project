from socket import *

HOST = '127.0.0.1'
PORT = 2021
BUF_SIZE = 1024
running = True

while running:

    command = input("Type a command: ").split()

    if command[0] == "quit":
        print("Program is finishing.")
        break

    if len(command) == 3 and command[0] == 'connect':

        s = socket(AF_INET, SOCK_STREAM)
        HOST = command[2]
        try:
            s.connect((HOST, PORT))
        except error as err:
            print(err)
            HOST = '127.0.0.1'
            continue

        with s:

            s.send(f"CONNECT {command[1]}".encode())
            response = s.recv(BUF_SIZE)
            print(response.decode())

            while True:
                command = input("Type a command: ").split()

                if len(command) == 1:

                    if command[0] == "disconnect":
                        s.send("DISCONNECT".encode())
                        response = s.recv(BUF_SIZE).decode()
                        if response == 'OK':
                            break
                        else:
                            print("Failed to disconnect.")

                    elif command[0] == "lu":
                        s.send("LU".encode())
                        response = s.recv(BUF_SIZE).decode()
                        print(response)

                    elif command[0] == "lf":
                        s.send("LF".encode())
                        response = s.recv(BUF_SIZE).decode()
                        print(response)

                    elif command[0] == "quit":
                        print("Program is finishing.")
                        running = False
                        break

                    else:
                        print("Wrong command! Try another pattern.")

                elif len(command) == 2:

                    if command[0] == "read":
                        s.send(f"READ {command[1]}".encode())
                        response = s.recv(BUF_SIZE).decode()
                        print(response)

                    elif command[0] == "write":
                        s.send(f"WRITE {command[1]}".encode())
                        response = s.recv(BUF_SIZE).decode()
                        print(response)

                    elif command[0] == "overread":
                        s.send(f"OVERREAD {command[1]}".encode())
                        response = s.recv(BUF_SIZE).decode()
                        print(response)

                    elif command[0] == "overwrite":
                        s.send(f"OVERWRITE {command[1]}".encode())
                        response = s.recv(BUF_SIZE).decode()
                        print(response)

                    else:
                        print("Wrong command! Try another pattern.")

                elif command[0] == "appendfile" and len(command) == 3:

                    s.send(f"APPENDFILE {command[1]} {command[2]}".encode())
                    response = s.recv(BUF_SIZE)
                    print(response.decode())

                elif command[0] == "send" and len(command) >=3:
                    message = ""
                    for i in range(2, len(command)):
                        message = message + command[i] + ' '
                    message = message.rstrip()
                    if message[0] == '"':
                        message = message[1:]
                    if message[-1] == '"':
                        message = message[:-1]
                    s.send(f"MESSAGE {command[1]}\n{len(message)} {message}".encode())
                    response = s.recv(BUF_SIZE)
                    print(response.decode())

                elif command[0] == "append" and len(command) >= 3:
                    s.send(f"APPEND {command[-1]}".encode())
                    response = s.recv(BUF_SIZE)
                    print(response.decode())

                else:
                    print("Wrong command! Try another pattern.")

    else:
        print("Wrong command! Correct pattern is 'connect USERNAME IP_ADDRESS'")
