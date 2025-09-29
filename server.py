import sys
import socket
import os
import threading
import pickle

FILE_MAX_TRANSFER = 512
DIR_CMD = "dir"
GET_CMD= "get"

def read_request(filename):
    opccode = 1

    return (opccode,0,filename)

def data(block_number,data):
    opccode = 3

    return (opccode,block_number,data)

def ack(block_number):
    opccode = 4

    return (opccode,block_number)

def validate_packet(packet, expected_opcode=None):
    """Validate packet structure and opcode"""
    if not isinstance(packet, tuple) or len(packet) < 1:
        return False
    if not isinstance(packet[0], int):
        return False
    if expected_opcode is not None and packet[0] != expected_opcode:
        return False
    return True

def err(error_string):
    opccode = 5

    return (opccode,error_string)

def receiveACK(socket,blockNumber):
    try:
        ack_packet_data = socket.recv(1024)
        if not ack_packet_data:
            socket.close()
            return False
        ack_packet = pickle.loads(ack_packet_data)
        if not validate_packet(ack_packet, 4) or len(ack_packet) < 2:
            socket.close()
            return False
        if ack_packet[1] != blockNumber:
            socket.close()
            return False
        return True
    except Exception:
        socket.close()
        return False
        

def thread_server(connectionSocket,addr):
    welcomeMsg = f"Welcome to {socket.gethostbyname(socket.gethostname())} file server"
    connectionSocket.send(pickle.dumps(data(0,welcomeMsg.encode("ascii"))))
    if not receiveACK(connectionSocket,0):
        return
    while True:
        try:
            request_data = connectionSocket.recv(1024)
            if not request_data:
                connectionSocket.close()
                return
            request = pickle.loads(request_data)
            if not validate_packet(request, 1) or len(request) < 3:
                connectionSocket.close()
                return
        except Exception:
            connectionSocket.close()
            return
        if(request[2]==""):
            i=0
            for i,fileName in enumerate(os.listdir('.')):
                connectionSocket.send(pickle.dumps(data(i+1,fileName.encode("ascii"))))
                if not receiveACK(connectionSocket,i+1):
                    return
            connectionSocket.send(pickle.dumps(data(i+1,b"")))
            receiveACK(connectionSocket,i+1)
        else:
            file_Name = request[2]
            if not os.path.exists(file_Name):
                error_msg = "File not found"
                connectionSocket.send(pickle.dumps(err(error_msg.encode("ascii"))))
            else:
                try:
                    with open(file_Name, 'rb') as file:
                        i = 1
                        while True:
                            chunk = file.read(FILE_MAX_TRANSFER)
                            connectionSocket.send(pickle.dumps(data(i,chunk)))
                            if not receiveACK(connectionSocket,i):
                                return
                            i += 1
                            if len(chunk) < 512:
                                break
                except Exception:
                    error_msg = "Error reading file"
                    connectionSocket.send(pickle.dumps(err(error_msg.encode("ascii"))))
                    



def main():
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Unable to start server")
        sys.exit(1)
    
    try:
        serverPort = int(sys.argv[1])
    except ValueError:
        print("Unable to start server")
        sys.exit(1)
    
    # Create TCP socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # utilizamos isto porque as vezes o bind pode ser encerrado abrutamente o que implica ficar em estado wait
    #assim mesmo wait ele pode ser reutilizado
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        serverSocket.bind(("", serverPort))
    except OSError as e:
        print(f"Unable to start server")
        sys.exit(1)
    
    serverSocket.listen(1)
    print("Server is running")
    
    while True:
        connectionSocket, addr = serverSocket.accept()

        tid = threading.Thread(target=thread_server, args=(connectionSocket,addr))
        tid.start()
    serverSocket.close()

if __name__ == "__main__":
    main()