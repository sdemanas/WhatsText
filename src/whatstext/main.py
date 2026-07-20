import atexit
import shutil
import signal
import sys
import tempfile
import webbrowser

from .server import create_server


def main():
    root_tmp = tempfile.mkdtemp(prefix="whatstext_")
    atexit.register(shutil.rmtree, root_tmp, ignore_errors=True)

    # atexit only runs on normal interpreter shutdown (Ctrl+C, return, uncaught
    # exception) — SIGTERM/SIGHUP default to killing the process immediately,
    # skipping atexit and leaving extracted media on disk. Route them through
    # sys.exit() so the atexit cleanup above still runs.
    def _terminate(signum, frame):
        sys.exit(0)

    signal.signal(signal.SIGTERM, _terminate)
    if hasattr(signal, "SIGHUP"):
        signal.signal(signal.SIGHUP, _terminate)

    httpd = create_server(root_tmp)
    port = httpd.server_address[1]
    url = f"http://127.0.0.1:{port}/"

    print(f"WhatsText is running at {url}")
    print("Drag your WhatsApp export .zip onto the page that just opened.")
    print("Press Ctrl+C to stop.")

    webbrowser.open(url)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
