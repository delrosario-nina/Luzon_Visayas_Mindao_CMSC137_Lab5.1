# sender.py
import socket
from crc_module import encode_data

RECEIVER_IP = "127.0.0.1"       # Replace with IP of the receiver 
PORT = 65432                    # Must match the receiver's port
KEY = "1001"                    # Must match the receiver 
NOMINEES = ["Nina", "Sam"]

def run_sender():
    fields = [f"AREA: {input('Area Code: ')}"]
    #for _ in range(int(input("Number of nominees: "))):
        #name = input(" Nominee name: ")
    for name in NOMINEES:
        votes = int(input(f" Total votes for {name}: "))
        fields.append(f"NOM:{name}: {votes}")
    fields.append(f"ELIG:{int(input('Total eligible voters: '))}")

    codewords = [encode_data(f, KEY)[0] for f in fields]      # CRC to EACH field
    message = "|".join(codewords)  

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((RECEIVER_IP, PORT))
        client_socket.sendall(message.encode("utf-8"))
        client_socket.shutdown(socket.SHUT_WR)              # Indicate that its done sending 
        status = client_socket.recv(1024).decode("utf-8")   # ACK / NACK from receiver
    print(f"[Sender] Receiver status: {status}")

if __name__ == "__main__":
    run_sender()


''' 
import socket
from crc_module import encode_data

def run_sender():
    # Agreed standard key representation (e.g., x^3 + 1 -> 1001)
    SHARED_KEY = "1001" 
    
    # Create client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 65432))
    
    payload = "Hello"
    encoded_bits, _ = encode_data(payload, SHARED_KEY)
    
    print(f"[Sender] Original text: {payload}")
    print(f"[Sender] Transmitting bits: {encoded_bits}")
    
    # Send raw binary string over the socket stream
    client_socket.sendall(encoded_bits.encode('utf-8'))
    
    # Wait for Receiver's Acknowledgement (ACK/NACK)
    response = client_socket.recv(1024).decode('utf-8')
    print(f"[Sender] Feedback from server: {response}")
    
    client_socket.close()

if __name__ == "__main__":
    run_sender()

'''

