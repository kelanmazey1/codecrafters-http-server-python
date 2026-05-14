import socket  # noqa: F401
import argparse
import threading
import app.router as router

from app.messages import req_resp_exchange
from app.directory import get_file_tree


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    args = get_cmd_line_args()


    root_dir = args.directory if args.directory else "/"
    f_tree = get_file_tree()
    f_tree.set_root(root_dir)

    router.collect_handlers()

    with socket.create_server(("localhost", 4221), reuse_port=True) as server:
        while True:
            conn, _ = server.accept()  # wait for client
            print(f"threads active: {threading.active_count()}")
            threading.Thread(
                target=req_resp_exchange, args=(conn,), daemon=True
            ).start()

def get_cmd_line_args() -> argparse.Namespace:
    # Get cmd line args
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--directory", required=False, type=str)
    return arg_parser.parse_args()


if __name__ == "__main__":
    main()

