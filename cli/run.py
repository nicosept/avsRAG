import argparse
import subprocess
import sys
import os
import signal


def launch():
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend"))
    frontend_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../frontend")
    )

    if os.name == "nt":  # Windows
        npm_cmd = "npm.cmd"

        # Risky, but without this modification to FastAPI kills the frontend process
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
    else:  # Unix/Linux/Mac
        npm_cmd = "npm"

    # Start FastAPI backend
    backend_proc = subprocess.Popen([sys.executable, "src/main.py"], cwd=backend_dir)

    # Start Vite frontend
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev", "--", "-l", "silent"], cwd=frontend_dir, creationflags=creationflags
    )

    # Implement better shutdown handling, Windows needs special handling
    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        backend_proc.terminate()
        try:
            if os.name == "nt":
                frontend_proc.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                frontend_proc.terminate()
        except Exception:
            pass
        frontend_proc.wait()


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
