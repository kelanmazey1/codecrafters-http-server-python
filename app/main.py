import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # TODO: Uncomment the code below to pass the first stage
    
    with socket.create_server(("localhost", 4221), reuse_port=True) as server:
        while True:
            conn, add = server.accept() # wait for client

            data = conn.recv(16384)
            if not data:
                continue
            else:
                conn.send(get_status_line("HTTP/1.1", 200, "OK"))



def get_status_line(protocol: str, code: int, reason_phrase: None | str = None):
    return f"{protocol} {code} {reason_phrase}\r\n\r\n".encode(encoding="utf-8")

if __name__ == "__main__":
    main()
