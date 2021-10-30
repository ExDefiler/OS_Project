from socket import *
from threading import *
import os

SERVER_FOLDER = r'D:\python\SERVER'
SERVER = gethostbyname(gethostname())
PORT = 2021
CLIENT_PORT = 2022
BUF_SIZE = 1024
CONNECTED_USERS = {}
mutex = Lock()

os.chdir(SERVER_FOLDER)
server = socket(AF_INET, SOCK_STREAM)
server.bind((SERVER, PORT))


def configure_directory():
    lf = os.listdir()
    for filename in lf:
        if ' ' in filename:
            mod_filename = filename.replace(' ', '_')
            os.rename(filename, mod_filename)


def client_handler(conn, address):

    connected = True
    msg_socket = socket(AF_INET, SOCK_STREAM)
    try:
        msg_socket.connect((address[0], CLIENT_PORT))
    except error:
        print("Failed to connect to client's message receiving port.")
        conn.send("ERROR\n".encode('ascii'))
        conn.close()
        msg_socket.close()
        return

    username = conn.recv(BUF_SIZE).decode('ascii').split()[1]
    mutex.acquire()
    if username in CONNECTED_USERS:
        conn.send("ERROR\n".encode('ascii'))
        conn.close()
        msg_socket.close()
        mutex.release()
        return
    mutex.release()

    print(f"[NEW CONNECTION] User {username}: {address} connected.")
    conn.send("OK\n".encode('ascii'))

    mutex.acquire()
    CONNECTED_USERS[username] = [msg_socket, Lock()]
    mutex.release()

    while connected:

        try:
            command = ''
            while '\n' not in command:
                packet = conn.recv(1).decode('ascii')
                if packet:
                    command += packet
                else:
                    connected = False
                    break
        except OSError as err:
            print(err)
            break

        command = command.split()

        if len(command) == 1:

            if command[0] == "DISCONNECT":
                if not CONNECTED_USERS[username][1].locked():
                    CONNECTED_USERS[username][1].acquire()
                    conn.send("OK\n".encode('ascii'))
                    break

                else:
                    conn.send("ERROR\n".encode('ascii'))

            elif command[0] == "LU":
                lu = ''
                mutex.acquire()
                for user in CONNECTED_USERS:
                    lu += user
                    lu += ' '
                mutex.release()
                lu = lu[:-1] + '\n'
                conn.send(lu.encode('ascii'))

            elif command[0] == "LF":
                lf = ''
                for filename in os.listdir():
                    lf += filename
                    lf += ' '
                lf = lf[:-1] + '\n'
                conn.send(lf.encode('ascii'))

            else:
                conn.send("ERROR\n".encode('ascii'))

        elif len(command) == 2:

            if command[0] == "READ":
                if command[1] in os.listdir() and os.path.isfile(command[1]):
                    conn.send("OK\n".encode('ascii'))
                    filesize = os.path.getsize(command[1])
                    conn.send(f'{str(filesize)} '.encode('ascii'))
                    with open(command[1], 'rb') as f:
                        filecontent = f.read()
                        conn.sendall(filecontent)
                else:
                    conn.send("ERROR\n".encode('ascii'))

            elif command[0] == "WRITE":
                if command[1] in os.listdir():
                    conn.send("ERROR\n".encode('ascii'))
                else:
                    conn.send("OK\n".encode('ascii'))
                    filesize = ''
                    while ' ' not in filesize:
                        char = conn.recv(1).decode('ascii')
                        filesize += char
                    filesize = int(filesize[:-1])
                    bytes_read = conn.recv(filesize)
                    with open(command[1], "wb") as f:
                        f.write(bytes_read)
                    if os.path.getsize(command[1]) == filesize:
                        conn.send("OK\n".encode('ascii'))
                    else:
                        conn.send("ERROR\n".encode('ascii'))

            elif command[0] == "OVERREAD":
                if command[1] in os.listdir() and os.path.isfile(command[1]):
                    conn.send("OK\n".encode('ascii'))
                    filesize = os.path.getsize(command[1])
                    conn.send(f'{str(filesize)} '.encode('ascii'))
                    with open(command[1], 'rb') as f:
                        filecontent = f.read()
                        conn.sendall(filecontent)
                else:
                    conn.send("ERROR\n".encode('ascii'))

            elif command[0] == "OVERWRITE":
                conn.send("OK\n".encode('ascii'))
                filesize = ''
                while ' ' not in filesize:
                    char = conn.recv(1).decode('ascii')
                    filesize += char
                filesize = int(filesize[:-1])
                bytes_read = conn.recv(filesize)
                with open(command[1], "wb") as f:
                    f.write(bytes_read)
                if os.path.getsize(command[1]) == filesize:
                    conn.send("OK\n".encode('ascii'))
                else:
                    conn.send("ERROR\n".encode('ascii'))

            elif command[0] == "APPEND":
                if command[1] in os.listdir() and os.path.isfile(command[1]):
                    conn.send("OK\n".encode('ascii'))
                    old_filesize = os.path.getsize(command[1])
                    filesize = ''
                    while ' ' not in filesize:
                        char = conn.recv(1).decode('ascii')
                        filesize += char
                    filesize = int(filesize[:-1])
                    content = conn.recv(filesize).decode('ascii')
                    with open(command[1], "a") as f:
                        f.write(content)
                    if os.path.getsize(command[1]) == filesize + old_filesize:
                        conn.send("OK\n".encode('ascii'))
                    else:
                        conn.send("ERROR\n".encode('ascii'))

                else:
                    conn.send("ERROR\n".encode('ascii'))

            elif command[0] == "MESSAGE":
                message_length = ''
                while ' ' not in message_length:
                    char = conn.recv(1).decode('ascii')
                    message_length += char
                message_length = int(message_length[:-1])
                message = conn.recv(message_length)
                mutex.acquire()
                if command[1] in CONNECTED_USERS:
                    CONNECTED_USERS[command[1]][0].send(f"MESSAGE\n{message_length} ".encode('ascii'))
                    CONNECTED_USERS[command[1]][0].send(message)
                    conn.send("OK\n".encode('ascii'))
                else:
                    conn.send("ERROR\n".encode('ascii'))
                mutex.release()

        elif len(command) == 3 and command[0] == "APPENDFILE":
            if command[2] in os.listdir():
                conn.send("OK\n".encode('ascii'))
                old_filesize = os.path.getsize(command[2])
                filesize = ''
                while ' ' not in filesize:
                    char = conn.recv(1).decode('ascii')
                    filesize += char
                filesize = int(filesize[:-1])
                bytes_read = conn.recv(filesize)
                with open(command[2], "ab") as f:
                    f.write(bytes_read)
                if os.path.getsize(command[2]) == filesize + old_filesize:
                    conn.send("OK\n".encode('ascii'))
                else:
                    conn.send("ERROR\n".encode('ascii'))

            else:
                conn.send("ERROR\n".encode('ascii'))

        else:
            conn.send("ERROR\n".encode('ascii'))

    conn.close()
    msg_socket.close()
    print(f"[END OF SESSION] User {username} disconnected.")

    mutex.acquire()
    CONNECTED_USERS.pop(username)
    mutex.release()


def start():

    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")

    while True:

        conn, address = server.accept()
        thread = Thread(target=client_handler, args=(conn, address))
        thread.start()


configure_directory()
print("[STARTING] Server is starting...")
start()
