import argparse
import os
import socket
import sys
from pathlib import Path

import uvicorn


PROJECT_DIR = Path(__file__).resolve().parent
os.chdir(PROJECT_DIR)
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


def main() -> None:
    parser = argparse.ArgumentParser(description="Start the Open Exam System backend")
    parser.add_argument("--host", default=os.getenv("OES_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("OES_PORT", "8000")))
    parser.add_argument("--reload", action="store_true", help="Enable development auto-reload")
    parser.add_argument("--strict-port", action="store_true", help="Fail instead of choosing the next free port")
    args = parser.parse_args()
    port = args.port
    if port != 0:
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
                probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                available = probe.connect_ex((args.host, port)) != 0
            if available or args.strict_port:
                break
            port += 1
        if not available:
            raise SystemExit(f"Port {args.port} is already in use. Choose another with --port.")
        if port != args.port:
            print(f"Port {args.port} is busy; using free port {port}.")
    uvicorn.run("main:app", host=args.host, port=port, reload=args.reload, log_level="info")


if __name__ == "__main__":
    main()