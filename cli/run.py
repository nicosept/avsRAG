import argparse
import subprocess
import sys
import os


def launch():
    backend_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../backend")
    )
    frontend_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../frontend")
    )

    if os.name == "nt":  # Windows
        npm_cmd = "npm.cmd"
    else:  # Unix/Linux/Mac
        npm_cmd = "npm"

    # Start FastAPI backend
    backend_proc = subprocess.Popen([sys.executable, "src/main.py"], cwd=backend_dir)

    # Start Vite frontend
    frontend_proc = subprocess.Popen([npm_cmd, "run", "dev", "--", "-l", "silent"], cwd=frontend_dir)

    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        backend_proc.terminate()
        frontend_proc.terminate()


def main():
    parser = argparse.ArgumentParser(prog="avsRAG")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("run", help="start backend + frontend")
    args = parser.parse_args()
    if args.cmd == "run":
        launch()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
