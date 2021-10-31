from socket import *
from threading import *
import os

SERVER_FOLDER = r'D:\python\SERVER'     # set path to your server folder here
SERVER = gethostbyname(gethostname())   # set IP address of your server here
PORT = 2021                             # configure your server's port
CLIENT_PORT = 2022                      # configure port for client messages
BUF_SIZE = 1024
INTERRUPTED = False                     # global var for catching SIGINT

FILES = {"read": [], "written": []}     # tracking files being read and being written
files_lock = Lock()

CONNECTED_USERS = {}                    # tracking connected users and their respective msg sockets
users_lock = Lock()

os.chdir(SERVER_FOLDER)
server = socket(AF_INET, SOCK_STREAM)
server.bind((SERVER, PORT))


def configure_directory():
    # eliminate spaces
    # from filenames
    lf = os.listdir()
    for filename in lf:
        if ' ' in filename:
            mod_filename = filename.replace(' ', '_')
            os.rename(filename, mod_filename)


def client_handler(conn, address):
    global INTERRUPTED

    if INTERRUPTED:
        conn.send("ERROR\n".encode('ascii'))
        return

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
    users_lock.acquire()
    if username in CONNECTED_USERS:
        conn.send("ERROR\n".encode('ascii'))
        conn.close()
        msg_socket.close()
        users_lock.release()
        return
    else:
        CONNECTED_USERS[username] = msg_socket
        users_lock.release()

    print(f"[NEW CONNECTION] User {username}: {address} connected.")
    conn.send("OK\n".encode('ascii'))

    while connected and not INTERRUPTED:

        try:
            conn.settimeout(2)
            command = ''
            while '\n' not in command and not INTERRUPTED:
                try:
                    packet = conn.recv(1).decode('ascii')
                except timeout:
                    continue

                if packet:
                    command += packet
                else:
                    connected = False
                    break
        except OSError as err:
            print(err)
            break

        if INTERRUPTED:
            conn.send("ERROR\n".encode('ascii'))
            msg_socket.send("DISCONNECT\n".encode('ascii'))
            break

        conn.settimeout(None)
        command = command.split()

        try:

            if len(command) == 1:

                if command[0] == "DISCONNECT":
                    code = users_lock.acquire(timeout=5)
                    if code:
                        conn.send("OK\n".encode('ascii'))
                        conn.close()
                        msg_socket.close()
                        print(f"[END OF SESSION] User {username} disconnected.")
                        CONNECTED_USERS.pop(username)
                        users_lock.release()
                        return

                    else:
                        conn.send("ERROR\n".encode('ascii'))

                elif command[0] == "LU":
                    lu = ''
                    users_lock.acquire()
                    for user in CONNECTED_USERS:
                        lu += user
                        lu += ' '
                    users_lock.release()
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
                    files_lock.acquire()
                    if command[1] in os.listdir() and os.path.isfile(command[1]) and command[1] not in FILES["written"]:
                        FILES["read"].append(command[1])
                        files_lock.release()

                        conn.send("OK\n".encode('ascii'))
                        filesize = os.path.getsize(command[1])
                        conn.send(f'{str(filesize)} '.encode('ascii'))
                        with open(command[1], 'rb') as f:
                            filecontent = f.read()
                            conn.sendall(filecontent)

                        files_lock.acquire()
                        FILES["read"].remove(command[1])
                        files_lock.release()

                    else:
                        files_lock.release()
                        conn.send("ERROR\n".encode('ascii'))

                elif command[0] == "WRITE":
                    files_lock.acquire()
                    if command[1] in os.listdir() or command[1] in FILES["written"]:
                        files_lock.release()
                        conn.send("ERROR\n".encode('ascii'))
                    else:
                        FILES["written"].append(command[1])
                        files_lock.release()

                        conn.send("OK\n".encode('ascii'))
                        filesize = ''
                        while ' ' not in filesize:
                            char = conn.recv(1).decode('ascii')
                            filesize += char
                        filesize = int(filesize[:-1])
                        bytes_read = conn.recv(filesize)

                        files_lock.acquire()
                        with open(command[1], "wb") as f:
                            f.write(bytes_read)
                        FILES["written"].remove(command[1])
                        if os.path.getsize(command[1]) == filesize:
                            conn.send("OK\n".encode('ascii'))
                        else:
                            conn.send("ERROR\n".encode('ascii'))
                        files_lock.release()

                elif command[0] == "OVERREAD":
                    files_lock.acquire()
                    if command[1] in os.listdir() and os.path.isfile(command[1]) and command[1] not in FILES["written"]:
                        FILES["read"].append(command[1])
                        files_lock.release()

                        conn.send("OK\n".encode('ascii'))
                        filesize = os.path.getsize(command[1])
                        conn.send(f'{str(filesize)} '.encode('ascii'))
                        with open(command[1], 'rb') as f:
                            filecontent = f.read()
                            conn.sendall(filecontent)

                        files_lock.acquire()
                        FILES["read"].remove(command[1])
                        files_lock.release()

                    else:
                        files_lock.release()
                        conn.send("ERROR\n".encode('ascii'))

                elif command[0] == "OVERWRITE":
                    files_lock.acquire()
                    if command[1] in FILES["written"] or command[1] in FILES["read"]:
                        files_lock.release()
                        conn.send("ERROR\n".encode('ascii'))
                    else:
                        FILES["written"].append(command[1])
                        files_lock.release()

                        conn.send("OK\n".encode('ascii'))
                        filesize = ''
                        while ' ' not in filesize:
                            char = conn.recv(1).decode('ascii')
                            filesize += char
                        filesize = int(filesize[:-1])
                        bytes_read = conn.recv(filesize)

                        files_lock.acquire()
                        with open(command[1], "wb") as f:
                            f.write(bytes_read)
                        FILES["written"].remove(command[1])
                        if os.path.getsize(command[1]) == filesize:
                            conn.send("OK\n".encode('ascii'))
                        else:
                            conn.send("ERROR\n".encode('ascii'))
                        files_lock.release()

                elif command[0] == "APPEND":
                    files_lock.acquire()
                    if command[1] in os.listdir() and os.path.isfile(command[1]) and \
                            command[1] not in FILES["read"] and command[1] not in FILES["written"]:
                        FILES["written"].append(command[1])
                        files_lock.release()

                        conn.send("OK\n".encode('ascii'))
                        old_filesize = os.path.getsize(command[1])
                        filesize = ''
                        while ' ' not in filesize:
                            char = conn.recv(1).decode('ascii')
                            filesize += char
                        filesize = int(filesize[:-1])
                        content = conn.recv(filesize).decode('ascii')

                        files_lock.acquire()
                        with open(command[1], "a") as f:
                            f.write(content)
                        FILES["written"].remove(command[1])
                        if os.path.getsize(command[1]) == filesize + old_filesize:
                            conn.send("OK\n".encode('ascii'))
                        else:
                            conn.send("ERROR\n".encode('ascii'))
                        files_lock.release()

                    else:
                        files_lock.release()
                        conn.send("ERROR\n".encode('ascii'))

                elif command[0] == "MESSAGE":
                    message_length = ''
                    while ' ' not in message_length:
                        char = conn.recv(1).decode('ascii')
                        message_length += char
                    message_length = int(message_length[:-1])
                    message = conn.recv(message_length)
                    users_lock.acquire()
                    if command[1] in CONNECTED_USERS:
                        CONNECTED_USERS[command[1]].send(f"MESSAGE\n{message_length} ".encode('ascii'))
                        CONNECTED_USERS[command[1]].send(message)
                        conn.send("OK\n".encode('ascii'))
                    else:
                        conn.send("ERROR\n".encode('ascii'))
                    users_lock.release()

            elif len(command) == 3 and command[0] == "APPENDFILE":
                files_lock.acquire()
                if command[2] in os.listdir() and os.path.isfile(command[2]) and \
                        command[2] not in FILES["read"] and command[2] not in FILES["written"]:
                    FILES["written"].append(command[2])
                    files_lock.release()
                    conn.send("OK\n".encode('ascii'))
                    old_filesize = os.path.getsize(command[2])
                    filesize = ''
                    while ' ' not in filesize:
                        char = conn.recv(1).decode('ascii')
                        filesize += char
                    filesize = int(filesize[:-1])
                    bytes_read = conn.recv(filesize)

                    files_lock.acquire()
                    with open(command[2], "ab") as f:
                        f.write(bytes_read)
                    FILES["written"].remove(command[2])
                    if os.path.getsize(command[2]) == filesize + old_filesize:
                        conn.send("OK\n".encode('ascii'))
                    else:
                        conn.send("ERROR\n".encode('ascii'))
                    files_lock.release()

                else:
                    files_lock.release()
                    conn.send("ERROR\n".encode('ascii'))

            else:
                conn.send("ERROR\n".encode('ascii'))

        except OSError as e:
            print(e)
            if files_lock.locked():
                files_lock.release()
            if users_lock.locked():
                users_lock.release()
            break

        if INTERRUPTED:
            msg_socket.send("DISCONNECT\n".encode('ascii'))
            break

    conn.close()
    msg_socket.close()
    print(f"[END OF SESSION] User {username} disconnected.")

    users_lock.acquire()
    CONNECTED_USERS.pop(username)
    users_lock.release()


def start():
    global INTERRUPTED

    server.listen()
    server.settimeout(2)
    print(f"[LISTENING] Server is listening on {SERVER}")
    initial_active = active_count()

    try:
        while True:
            try:
                conn, address = server.accept()
            except timeout:
                continue
            thread = Thread(target=client_handler, args=(conn, address))
            thread.start()

    except KeyboardInterrupt:
        INTERRUPTED = True
        while active_count() > initial_active:
            pass
        print("[TERMINATING] Process terminated via KeyboardInterrupt.")


configure_directory()
print("[STARTING] Server is starting...")
start()
