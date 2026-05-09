import socket  # noqa: F401
from app.messages import HTTPRequest, HTTPResponse, HTTPResponseLine
import app.router as router


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    with socket.create_server(("localhost", 4221), reuse_port=True) as server:
        while True:
            conn, add = server.accept() # wait for client
        
            req = HTTPRequest.from_bytes(conn.recv(16384))

            router.collect_handlers()
            r = router.get_router()
            
            handler_tup = r.resolve(req.get_path())

            # If path can't be resolved by router
            if handler_tup is None:
                resp = HTTPResponse(response_line=HTTPResponseLine(404, "Not Found"))
            else:
                handler, params = handler_tup
                resp = handler(params)

            conn.send(resp.to_bytes())
            conn.send(b"\r\n")




if __name__ == "__main__":
    main()
