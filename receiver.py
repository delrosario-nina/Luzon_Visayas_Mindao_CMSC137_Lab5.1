# receiver.py
import socket
from crc_module import mod2div

def run_receiver():
    SHARED_KEY = "1001"
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 65432))    # Replace with IP of the receiver
    server_socket.listen(1)
    print("[Receiver] Server listening for connections...")
    
    conn, addr = server_socket.accept()
    print(f"[Receiver] Connected to: {addr}")
    
    # Receive raw stream bit data (keep reading until the sender is done)
    received_bits = ""
    while True:
        chunk = conn.recv(1024).decode('utf-8')
        if not chunk:
            break
        received_bits += chunk
    if not received_bits:
        return
        
    print(f"[Receiver] String bits received: {received_bits}")
    
    # Each field has its own CRC, fields are separated by '|'
    error = False
    fields = []
    for codeword in received_bits.split("|"):
        # Compute remainder using the entire field (data + checksum appended)
        remainder = mod2div(codeword, SHARED_KEY)
        print(f"[Receiver] Remainder calculated: {remainder}")
        
        # If any bit is '1', an error occurred in transmission
        if "1" in remainder:
            error = True
            break
        
        # Remove the checksum bits and convert the data bits back to text
        data_bits = codeword[:-(len(SHARED_KEY) - 1)]
        fields.append("".join(chr(int(data_bits[i:i+8], 2)) for i in range(0, len(data_bits), 8)))
    
    if error:
        print("[Receiver] Error detected via CRC! Data corrupted. Disregarding all data.")
        conn.sendall("NACK: Data Corrupted".encode('utf-8'))
    else:
        print("[Receiver] Checksum valid. Data received successfully.")
        conn.sendall("ACK: Data Verified".encode('utf-8'))
        
        # Add the votes
        votes = {}
        eligible = 0
        for field in fields:
            kind, _, rest = field.partition(":")
            if kind == "NOM":
                name, _, v = rest.rpartition(":")
                votes[name.strip()] = int(v)
            elif kind == "ELIG":
                eligible = int(rest)
        total = sum(votes.values())
        
        # Show each nominee (highest votes first) with percentage
        print(f"\n{'Nominee':<20}{'Votes':>8}{'Percent':>10}")
        for name, v in sorted(votes.items(), key=lambda x: x[1], reverse=True):
            print(f"{name:<20}{v:>8}{v / (total or 1) * 100:>9.2f}%")
        print(f"\nTotal votes: {total}")
        print(f"Voters who voted: {total / (eligible or 1) * 100:.2f}% of {eligible} eligible")
        
    conn.close()
    server_socket.close()

if __name__ == "__main__":
    run_receiver()

'''
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

'''