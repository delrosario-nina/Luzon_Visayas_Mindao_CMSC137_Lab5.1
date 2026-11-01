# receiver.py
import socket
from crc_module import mod2div

def run_receiver():
    SHARED_KEY = "1001"
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 65432))
    server_socket.listen(1)
    print("[Receiver] Server listening for connections...")
    
    conn, addr = server_socket.accept()
    print(f"[Receiver] Connected to: {addr}")
    
    # Receive raw stream bit data
    received_bits = conn.recv(1024).decode('utf-8')
    if not received_bits:
        return
        
    print(f"[Receiver] String bits received: {received_bits}")
    
    # Compute remainder using the entire payload (data + checksum appended)
    remainder = mod2div(received_bits, SHARED_KEY)
    print(f"[Receiver] Remainder calculated: {remainder}")
    
    # If any bit is '1', an error occurred in transmission
    if "1" in remainder:
        print("[Receiver] Error detected via CRC! Data corrupted.")
        conn.sendall("NACK: Data Corrupted".encode('utf-8'))
    else:
        print("[Receiver] Checksum valid. Data received successfully.")
        conn.sendall("ACK: Data Verified".encode('utf-8'))
        
    conn.close()
    server_socket.close()

if __name__ == "__main__":
    run_receiver()