# sender.py
import socket
from crc_module import encode_data

RECEIVER_IP = "192.168.x.x"     # Replace with IP of the receiver 
PORT = 65432                    # Must match the receiver's port
KEY = "1001"                    # Must match the receiver 

def run_sender():
    fields = [f"AREA: {input('Area Code: ')}"]
    for _ in range(int(input("Number of nominees: "))):
        name = input(" Nominee name: ")
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