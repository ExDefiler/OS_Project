from socket import *
from threading import *

HOST = gethostbyname(gethostname())
PORT_SEND = 2021
PORT_RCV = 2022
BUF_SIZE = 1024
print_screen = Lock()


def message_thread():

    rcv_socket = socket(AF_INET, SOCK_STREAM)
    rcv_socket.bind((HOST, PORT_RCV))
    rcv_socket.listen()
    conn, address = rcv_socket.accept()

    while True:
        try:
            message = conn.recv(BUF_SIZE).decode()
        except error as e:
            print_screen.acquire()
            print(e)
            print_screen.release()
            conn.close()
            rcv_socket.close()
            break

        if message:
            print_screen.acquire()
            print(message)
            print_screen.release()

        else:
            conn.close()
            rcv_socket.close()
            break


def protocol_thread(sock, username):
    global running

    with sock:

        sock.send(f"CONNECT {username}".encode())
        response = sock.recv(BUF_SIZE)
        print_screen.acquire()
        print(response.decode())
        print_screen.release()

        while True:
            print_screen.acquire()
            command = input("Type a command: ").split()
            print_screen.release()

            if len(command) == 1:

                if command[0] == "disconnect":
                    sock.send("DISCONNECT".encode())
                    response = sock.recv(BUF_SIZE).decode()
                    if response == 'OK':
                        break
                    else:
                        print_screen.acquire()
                        print("Failed to disconnect.")
                        print_screen.release()

                elif command[0] == "lu":
                    sock.send("LU".encode())
                    response = sock.recv(BUF_SIZE).decode()
                    print_screen.acquire()
                    print(response)
                    print_screen.release()

                elif command[0] == "lf":
                    sock.send("LF".encode())
                    response = sock.recv(BUF_SIZE).decode()
                    print_screen.acquire()
                    print(response)
                    print_screen.release()

                elif command[0] == "quit":
                    print_screen.acquire()
                    print("Program is finishing.")
                    print_screen.release()
                    running = False
                    break

                else:
                    print_screen.acquire()
                    print("Wrong command! Try another pattern.")
                    print_screen.release()

            elif len(command) == 2:

                if command[0] == "read":
                    sock.send(f"READ {command[1]}".encode())
                    response = sock.recv(BUF_SIZE).decode()
                    print_screen.acquire()
                    print(response)
                    print_screen.release()

                elif command[0] == "write":
                    sock.send(f"WRITE {command[1]}".encode())
                    response = sock.recv(BUF_SIZE).decode()
                    print_screen.acquire()
                    print(response)
                    print_screen.release()

                elif command[0] == "overread":
                    sock.send(f"OVERREAD {command[1]}".encode())
                    response = sock.recv(BUF_SIZE).decode()
                    print_screen.acquire()
                    print(response)
                    print_screen.release()

                elif command[0] == "overwrite":
                    sock.send(f"OVERWRITE {command[1]}".encode())
                    response = sock.recv(BUF_SIZE).decode()
                    print_screen.acquire()
                    print(response)
                    print_screen.release()

                else:
                    print_screen.acquire()
                    print("Wrong command! Try another pattern.")
                    print_screen.release()

            elif command[0] == "appendfile" and len(command) == 3:

                sock.send(f"APPENDFILE {command[1]} {command[2]}".encode())
                response = sock.recv(BUF_SIZE)
                print_screen.acquire()
                print(response.decode())
                print_screen.release()

            elif command[0] == "send" and len(command) >= 3:
                message = ""
                for i in range(2, len(command)):
                    message = message + command[i] + ' '
                message = message.rstrip()
                if message[0] == '"':
                    message = message[1:]
                if message[-1] == '"':
                    message = message[:-1]
                sock.send(f"MESSAGE {command[1]}\n{len(message)} {message}".encode())
                response = sock.recv(BUF_SIZE)
                print_screen.acquire()
                print(response.decode())
                print_screen.release()

            elif command[0] == "append" and len(command) >= 3:
                sock.send(f"APPEND {command[-1]}".encode())
                response = sock.recv(BUF_SIZE)
                print_screen.acquire()
                print(response.decode())
                print_screen.release()

            else:
                print_screen.acquire()
                print("Wrong command! Try another pattern.")
                print_screen.release()


running = True

while running:

    instruction = input("Type a command: ").split()

    if instruction[0] == "quit":
        print("Program is finishing.")
        break

    if len(instruction) == 3 and instruction[0] == 'connect':

        s = socket(AF_INET, SOCK_STREAM)
        try:
            s.connect((instruction[2], PORT_SEND))
        except error as err:
            print(err)
            continue

        t1 = Thread(target=protocol_thread, args=(s, instruction[1]))
        t2 = Thread(target=message_thread)

        t2.start()
        t1.start()
        t1.join()
        t2.join()

    else:
        print("Wrong command! Correct pattern is 'connect USERNAME IP_ADDRESS'")
