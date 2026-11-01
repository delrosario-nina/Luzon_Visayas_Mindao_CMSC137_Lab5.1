# sender.py
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