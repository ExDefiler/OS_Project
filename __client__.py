from socket import *
from threading import *
import os

CLIENT_FOLDER = r'D:\python\CLIENT'
HOST = gethostbyname(gethostname())
PORT_SEND = 2021
PORT_RCV = 2022
BUF_SIZE = 1024
print_screen = Lock()
running = True
connected = False
os.chdir(CLIENT_FOLDER)


def configure_directory():
    # eliminate spaces
    # from filenames
    lf = os.listdir()
    for filename in lf:
        if ' ' in filename:
            mod_filename = filename.replace(' ', '_')
            os.rename(filename, mod_filename)


def print_response(socket_object):

    response = socket_object.recv(BUF_SIZE).decode('ascii')
    print_screen.acquire()
    print(response)
    print_screen.release()
    return response


def message_thread():
    global connected

    rcv_socket = socket(AF_INET, SOCK_STREAM)
    rcv_socket.bind((HOST, PORT_RCV))
    rcv_socket.listen()
    conn, address = rcv_socket.accept()

    while connected:

        try:
            message = ''
            while '\n' not in message:

                packet = conn.recv(1).decode('ascii')

                if packet:
                    message += packet

                else:
                    connected = False
                    break

        except OSError as e:
            print(e)
            connected = False
            break

        if message == "DISCONNECT\n":
            connected = False

        elif message == "MESSAGE\n":
            message_length = ''
            while ' ' not in message_length:
                char = conn.recv(1).decode('ascii')
                message_length += char
            message_length = int(message_length[:-1])
            message = conn.recv(message_length).decode('ascii')
            print_screen.acquire()
            print(message)
            print_screen.release()

    conn.close()
    rcv_socket.close()


def protocol_thread(client_socket, username):
    global running
    global connected

    with client_socket:

        client_socket.send(f"CONNECT {username}\n".encode('ascii'))
        response = print_response(client_socket)
        if response == "ERROR\n":
            connected = False
            return

        while connected:
            print_screen.acquire()
            command = input("[CONNECTED] Type a command: ").split()
            print_screen.release()

            if not connected:
                continue

            try:

                if len(command) == 1:

                    if command[0] == "disconnect":
                        client_socket.send("DISCONNECT\n".encode('ascii'))
                        response = client_socket.recv(BUF_SIZE).decode('ascii')
                        if response == 'OK\n':
                            connected = False
                            break
                        else:
                            print_screen.acquire()
                            print("Failed to disconnect.")
                            print_screen.release()

                    elif command[0] == "lu":
                        client_socket.send("LU\n".encode('ascii'))
                        print_response(client_socket)

                    elif command[0] == "lf":
                        client_socket.send("LF\n".encode('ascii'))
                        print_response(client_socket)

                    elif command[0] == "quit":
                        print_screen.acquire()
                        print("Program is finishing.")
                        print_screen.release()
                        connected = False
                        running = False
                        break

                    else:
                        print_screen.acquire()
                        print("Wrong command! Try another pattern.\n")
                        print_screen.release()

                elif len(command) == 2:

                    if command[0] == "read":
                        if command[1] in os.listdir():
                            print(f"[FILENAME ERROR] The directory already contains a file with name: {command[1]}\n")
                            continue
                        client_socket.send(f"READ {command[1]}\n".encode('ascii'))
                        response = print_response(client_socket)
                        if response == "OK\n":
                            filesize = ''
                            while ' ' not in filesize:
                                char = client_socket.recv(1).decode('ascii')
                                filesize += char
                            filesize = int(filesize[:-1])
                            bytes_read = client_socket.recv(filesize)
                            with open(command[1], "wb") as f:
                                f.write(bytes_read)

                    elif command[0] == "write":
                        if command[1] in os.listdir():
                            client_socket.send(f"WRITE {command[1]}\n".encode('ascii'))
                            response = print_response(client_socket)
                            if response == "OK\n":
                                filesize = os.path.getsize(command[1])
                                client_socket.send(f'{str(filesize)} '.encode('ascii'))
                                with open(command[1], 'rb') as f:
                                    filecontent = f.read()
                                    client_socket.sendall(filecontent)
                                print_response(client_socket)
                        else:
                            print(f"[FILENAME ERROR] The directory contains no file with name: {command[1]}\n")

                    elif command[0] == "overread":
                        client_socket.send(f"OVERREAD {command[1]}\n".encode('ascii'))
                        response = print_response(client_socket)
                        if response == "OK\n":
                            filesize = ''
                            while ' ' not in filesize:
                                char = client_socket.recv(1).decode('ascii')
                                filesize += char
                            filesize = int(filesize[:-1])
                            bytes_read = client_socket.recv(filesize)
                            with open(command[1], "wb") as f:
                                f.write(bytes_read)

                    elif command[0] == "overwrite":
                        if command[1] in os.listdir():
                            client_socket.send(f"OVERWRITE {command[1]}\n".encode('ascii'))
                            response = print_response(client_socket)
                            if response == "OK\n":
                                filesize = os.path.getsize(command[1])
                                client_socket.send(f'{str(filesize)} '.encode('ascii'))
                                with open(command[1], 'rb') as f:
                                    filecontent = f.read()
                                    client_socket.sendall(filecontent)
                                print_response(client_socket)
                        else:
                            print(f"[FILENAME ERROR] The directory contains no file with name: {command[1]}\n")

                    else:
                        print_screen.acquire()
                        print("Wrong command! Try another pattern.\n")
                        print_screen.release()

                elif command[0] == "appendfile" and len(command) == 3:
                    if command[1] not in os.listdir():
                        print(f"[FILENAME ERROR] The directory contains no file with name: {command[1]}\n")
                        continue

                    client_socket.send(f"APPENDFILE {command[1]} {command[2]}\n".encode('ascii'))
                    response = print_response(client_socket)
                    if response == "OK\n":
                        filesize = os.path.getsize(command[1])
                        client_socket.send(f'{str(filesize)} '.encode('ascii'))
                        with open(command[1], 'rb') as f:
                            filecontent = f.read()
                            client_socket.sendall(filecontent)
                        print_response(client_socket)

                elif command[0] == "send" and len(command) >= 3:

                    if command[2].startswith('"') and command[-1].endswith('"'):
                        message = ''
                        for i in range(2, len(command)):
                            message = message + command[i] + ' '
                        message = message.strip('" ')
                        client_socket.send(f"MESSAGE {command[1]}\n{len(message.encode('ascii'))} {message}".encode('ascii'))
                        print_response(client_socket)

                    else:
                        print('The message to be sent must come inside double quotation marks: "..."')

                elif command[0] == "append" and len(command) >= 3:

                    if command[1].startswith('"') and command[-2].endswith('"'):
                        client_socket.send(f"APPEND {command[-1]}\n".encode())
                        response = print_response(client_socket)
                        if response == "OK\n":
                            content = ''
                            for word in command[1:-1]:
                                content += word
                                content += ' '
                            content = content.strip('" ')
                            content = content.encode('ascii')
                            client_socket.send(f"{str(len(content))} ".encode('ascii'))
                            client_socket.send(content)
                            print_response(client_socket)

                    else:
                        print('The content to be appended must come inside double quotation marks: "..."')

                else:
                    print_screen.acquire()
                    print("Wrong command! Try another pattern.\n")
                    print_screen.release()

            except OSError as e:
                print(e)
                connected = False
                break


configure_directory()
while running:

    instruction = input("[NOT CONNECTED] Type a command: ").split()

    if instruction[0] == "quit":
        print("Program is finishing.")
        break

    if len(instruction) == 3 and instruction[0] == 'connect':

        s = socket(AF_INET, SOCK_STREAM)
        try:
            s.connect((instruction[2], PORT_SEND))
            connected = True
        except OSError as err:
            print(err)
            continue

        prt_thread = Thread(target=protocol_thread, args=(s, instruction[1]))
        msg_thread = Thread(target=message_thread)
        msg_thread.start()
        prt_thread.start()
        prt_thread.join()
        msg_thread.join()

    else:
        print("Wrong command! Correct pattern is 'connect USERNAME IP_ADDRESS'\n")
