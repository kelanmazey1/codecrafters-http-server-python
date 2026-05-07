import socket  # noqa: F401
from app.request import HTTPRequest, HTTPResponse, HTTPResponseLine


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    with socket.create_server(("localhost", 4221), reuse_port=True) as server:
        while True:
            conn, add = server.accept() # wait for client
        
            req = HTTPRequest.from_tcp(conn.recv(16384))
            if req.get_path().exists():
                resp = HTTPResponse(response_line=HTTPResponseLine(200, "OK"))
            else:
                resp = HTTPResponse(response_line=HTTPResponseLine(404, "Not Found"))
            conn.send(resp.get_response_line_bytes())
            conn.send(b"\r\n")







if __name__ == "__main__":
    main()
