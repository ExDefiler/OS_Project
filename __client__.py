
running = True

while running:

    command = input("Type a command: ").split()

    if command[0] == "quit":
        print("Program is finishing.")
        break

    if len(command) == 3 and command[0] == 'connect':
        print(f"CONNECT {command[1]}")

        while True:
            command = input("Type a command: ").split()

            if len(command) == 1:

                if command[0] == "disconnect":
                    print("DISCONNECT")
                    break

                elif command[0] == "lu":
                    print("LU")

                elif command[0] == "lf":
                    print("LF")

                elif command[0] == "quit":
                    print("Program is finishing.")
                    running = False
                    break

                else:
                    print("Wrong command! Try another pattern.")

            elif len(command) == 2:

                if command[0] == "read":
                    print(f"READ {command[1]}")

                elif command[0] == "write":
                    print(f"WRITE {command[1]}")

                elif command[0] == "overread":
                    print(f"OVERREAD {command[1]}")

                elif command[0] == "overwrite":
                    print(f"OVERWRITE {command[1]}")

                else:
                    print("Wrong command! Try another pattern.")

            elif command[0] == "appendfile" and len(command) == 3:

                print(f"APPENDFILE {command[1]} {command[2]}")

            elif command[0] == "send" and len(command) >= 3:
                message = ""
                for i in range(2, len(command)):
                    message = message + command[i] + ' '
                message = message.rstrip()
                if message[0] == '"':
                    message = message[1:]
                if message[-1] == '"':
                    message = message[:-1]
                print(f"MESSAGE {command[1]}\n{len(message)} {message}")

            elif command[0] == "append" and len(command) >= 3:
                print(f"APPEND {command[-1]}")
                print("NUMBER_OF_BYTES FILE_CONTENT")

            else:
                print("Wrong command! Try another pattern.")

    else:
        print("Wrong command! Correct pattern is 'connect USERNAME IP_ADDRESS'")
