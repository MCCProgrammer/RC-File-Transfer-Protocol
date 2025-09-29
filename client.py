import sys
import socket
import os
import pickle

def send_request(content):
    opccode = 1
    # RRQ: opcode, block_number (unused -> 0), filename (empty for dir)
    return (opccode,0,content)

def data(block_number,data):
    opccode = 3

    return (opccode,block_number,data)

def ack(block_number):
    opccode = 4

    return (opccode,block_number)

def err(error_string):
    opccode = 5

    return (opccode,error_string)

def validate_packet(packet, expected_opcode=None):
    """Validate packet structure and opcode"""
    if not isinstance(packet, tuple) or len(packet) < 1:
        return False
    if not isinstance(packet[0], int):
        return False
    if expected_opcode is not None and packet[0] != expected_opcode:
        return False
    return True

def sendACK(blockNumber,connSocket):
    connSocket.send(pickle.dumps((4,blockNumber)))



def main():
    # Check command line arguments
    if len(sys.argv) != 3:
        # Keep quiet per spec; just exit on bad invocation
        sys.exit(1)
    
    serverAdress = sys.argv[1]
    try:
        serverPort = int(sys.argv[2])
    except ValueError:
        sys.exit(1)

    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        clientSocket.connect((serverAdress, serverPort))
    except Exception:
        print("Unable to connect with the server")
        sys.exit(1)

    print("Connect to server")

    # Greeting
    welcome_data = clientSocket.recv(1024)
    welcome_packet = pickle.loads(welcome_data)
    if not validate_packet(welcome_packet, 3) or len(welcome_packet) < 3 or welcome_packet[1] != 0:
        clientSocket.close()
        sys.exit(1)
    print(welcome_packet[2].decode('ascii'))
    sendACK(welcome_packet[1],clientSocket)

    while True:
        cmd = input("client>")
        if not cmd:
            continue
        cmdArray = cmd.split()
        command = cmdArray[0]
        if command == "dir":
            if len(cmdArray) != 1:
                print("Unknown command")
                continue
            clientSocket.send(pickle.dumps(send_request("")))
            while True:
                rawData = clientSocket.recv(1024)
                dataTuple = pickle.loads(rawData)
                if dataTuple[0] == 5:
                    # error message
                    err_msg = dataTuple[1].decode('ascii') if isinstance(dataTuple[1], bytes) else dataTuple[1]
                    print(err_msg)
                    break
                if not validate_packet(dataTuple, 3) or len(dataTuple) < 3:
                    clientSocket.close()
                    sys.exit(1)
                block_no = dataTuple[1] 
                payload = dataTuple[2]
                if len(payload) > 0:
                    print(payload.decode('ascii'))
                sendACK(block_no,clientSocket)
                if len(payload) == 0:
                    break
        elif command == "get":
            if len(cmdArray) != 3:
                print("Unknown command")
                continue
            remoteFile = cmdArray[1]
            localFile = cmdArray[2]
            if os.path.exists(localFile):
                print("Unknown command")
                continue
            clientSocket.send(pickle.dumps(send_request(remoteFile)))
            with open(localFile, 'wb') as file:
                client_block_number = 1
                while True:
                    rawData = clientSocket.recv(1024)
                    dataTuple = pickle.loads(rawData)
                    if dataTuple[0] == 5:
                        # Server-side error (e.g., file not found)
                        err_msg = dataTuple[1].decode('ascii') if isinstance(dataTuple[1], bytes) else dataTuple[1]
                        print("Unknown command")
                        file.close()
                        os.remove(localFile)
                        break
                    if not validate_packet(dataTuple, 3) or len(dataTuple) < 3:
                        clientSocket.close()
                        file.close()
                        os.remove(localFile)
                        sys.exit(1)
                    if dataTuple[1] != client_block_number:
                        clientSocket.close()
                        file.close()
                        os.remove(localFile)
                        sys.exit(1)
                    file.write(dataTuple[2])
                    sendACK(client_block_number,clientSocket)
                    if len(dataTuple[2]) < 512:
                        print("File transfer completed")
                        break
                    client_block_number += 1
        elif command == "end":
            print("Connection close, client ended")
            clientSocket.close()
            break
        else:
            print("Unknown command")

if __name__ == "__main__":
    main()