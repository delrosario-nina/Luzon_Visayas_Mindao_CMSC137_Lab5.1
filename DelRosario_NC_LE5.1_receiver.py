# receiver.py
import socket
from crc_module import mod2div

HOST = "127.0.0.1"              # Replace with IP of the receiver
PORT = 65432                    # Must match the sender's port
KEY = "1001"                    # Must match the sender
NOMINEES = ["Nina", "Sam"]      # Must match the sender

def decode(codeword):
    """Returns the original text, or None if the CRC check fails."""
    if "1" in mod2div(codeword, KEY):
        return None
    bits = codeword[:-(len(KEY) - 1)]
    return "".join(chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8))

def run_receiver():
    totals = {name: 0 for name in NOMINEES}     # hardcoded nominees
    #totals = {}                                # no hardcoded nominees
    eligible = 0

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        server_socket.settimeout(1)             # wake up every second so Ctrl+C works
        print("[Receiver] Server listening for connections... (Ctrl+C to stop)")

        while True:                             # keep running: one sender (precinct) at a time
            try:
                conn, addr = server_socket.accept()
            except socket.timeout:              # nobody connected this second, keep waiting
                continue
            with conn:
                print(f"\n[Receiver] Connected to: {addr}")
                message = ""
                while True:                     # read until the sender is done
                    chunk = conn.recv(1024).decode("utf-8")
                    if not chunk:
                        break
                    message += chunk
                if not message:
                    continue

                # CRC check on EACH field; one error = disregard everything
                fields = [decode(cw) for cw in message.split("|")]
                if None in fields:
                    print("[Receiver] Error detected via CRC! Data disregarded.")
                    conn.sendall("NACK: Data Corrupted".encode("utf-8"))
                    continue
                conn.sendall("ACK: Data Verified".encode("utf-8"))

                # Add the votes to the running totals
                for field in fields:
                    kind, _, rest = field.partition(":")
                    if kind == "AREA":
                        print(f"[Receiver] Area{rest} reported")
                    elif kind == "NOM":
                        name, _, votes = rest.rpartition(":")
                        totals[name.strip()] = totals.get(name.strip(), 0) + int(votes)
                    elif kind == "ELIG":
                        eligible += int(rest)

                # Show totals, highest first
                total = sum(totals.values())
                print(f"{'Nominee':<15}{'Votes':>8}{'Percent':>10}")
                for name, votes in sorted(totals.items(), key=lambda x: x[1], reverse=True):
                    print(f"{name:<15}{votes:>8}{votes / (total or 1) * 100:>9.2f}%")
                print(f"Total votes: {total}")
                print(f"Voters who voted: {total / (eligible or 1) * 100:.2f}% of {eligible} eligible")

if __name__ == "__main__":
    try:
        run_receiver()
    except KeyboardInterrupt:
        print("\n[Receiver] Shutting down.")