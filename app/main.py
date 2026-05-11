import socket  # noqa: F401
import argparse
import threading
import app.router as router
from app.messages import HTTPRequest, HTTPResponse, HTTPResponseLine
from app.directory import get_file_tree


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--directory", required=False, type=str)
    args = arg_parser.parse_args()

    root_dir = args.directory if args.directory else "/"
    f_tree = get_file_tree()
    f_tree.set_root(root_dir)

    router.collect_handlers()

    with socket.create_server(("localhost", 4221), reuse_port=True) as server:
        while True:
            conn, add = server.accept()  # wait for client

            threading.Thread(
                target=req_resp_exchange, args=(conn,), daemon=True
            ).start()


def req_resp_exchange(conn: socket.socket):
    req = HTTPRequest.from_bytes(conn.recv(16384))

    r = router.get_router()
    handler_tup = r.resolve(req.get_path(), req.get_request_type())

    # If path can't be resolved by router
    if handler_tup is None:
        resp = HTTPResponse(response_line=HTTPResponseLine(404, "Not Found"))
    else:
        handler, params = handler_tup
        try:
            resp = handler(params, req)
        except TypeError as err:
            raise TypeError(
                "Handlers must have the function signature handler(params: dict[str, Any], req: HTTPRequest) -> HTTPResponse"
            ) from err

    conn.send(resp.to_bytes())
    conn.send(b"\r\n")


if __name__ == "__main__":
    main()
