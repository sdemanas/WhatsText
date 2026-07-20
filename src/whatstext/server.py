import html
import mimetypes
import os
import re
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from string import Template
from urllib.parse import parse_qs, quote, unquote, urlsplit

from . import extractor, generator, sanitizer, textparser

PACKAGE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = PACKAGE_DIR / "assets" / "templates"
STATIC_DIR = PACKAGE_DIR / "assets" / "static"

MIME_OVERRIDES = {
    ".webp": "image/webp",
    ".opus": "audio/ogg",
    ".3gp": "video/3gpp",
    ".m4a": "audio/mp4",
}

UPLOAD_CHUNK = 1024 * 1024

# session_id -> {"grouped": dict, "files_dir": str, "participants": list[str], "output_dir": str}
SESSIONS = {}


def _safe_join(base_dir, relpath):
    base = os.path.realpath(base_dir)
    target = os.path.realpath(os.path.join(base, relpath))
    if os.path.commonpath([base, target]) != base:
        return None
    return target


def _guess_content_type(path):
    ext = os.path.splitext(path)[1].lower()
    return MIME_OVERRIDES.get(ext) or mimetypes.guess_type(path)[0] or "application/octet-stream"


class WhatsTextHandler(BaseHTTPRequestHandler):
    root_tmp = None

    def log_message(self, fmt, *args):
        pass

    # -- helpers ---------------------------------------------------------

    def _send_text(self, status, body, content_type="text/plain; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_file(self, path):
        if not os.path.isfile(path):
            self.send_error(404)
            return

        size = os.path.getsize(path)
        content_type = _guess_content_type(path)
        start, end = 0, size - 1
        status = 200

        range_header = self.headers.get("Range")
        if range_header:
            match = re.match(r"bytes=(\d*)-(\d*)", range_header)
            if match:
                start_s, end_s = match.groups()
                start = int(start_s) if start_s else 0
                end = int(end_s) if end_s else size - 1
                status = 206

        if size == 0:
            start, end = 0, -1
        elif start >= size or end >= size or start > end:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.end_headers()
            return

        length = end - start + 1

        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("Accept-Ranges", "bytes")
        if status == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()

        if length <= 0:
            return

        with open(path, "rb") as f:
            f.seek(start)
            remaining = length
            while remaining > 0:
                chunk = f.read(min(UPLOAD_CHUNK, remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)

    def _redirect(self, location):
        self.send_response(303)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        self.end_headers()

    # -- routing -----------------------------------------------------------

    def do_GET(self):
        parsed = urlsplit(self.path)
        path = unquote(parsed.path)
        query = parse_qs(parsed.query)

        if path in ("/", "/index.html"):
            self._send_file(TEMPLATES_DIR / "drop.html")
            return

        if path.startswith("/static/"):
            target = _safe_join(STATIC_DIR, path[len("/static/"):])
            if not target:
                self.send_error(404)
                return
            self._send_file(target)
            return

        m = re.match(r"^/chat/([a-f0-9]+)/pick-sender$", path)
        if m:
            self._handle_pick_sender(m.group(1), query)
            return

        m = re.match(r"^/chat/([a-f0-9]+)/(.*)$", path)
        if m:
            self._serve_session_file(m.group(1), m.group(2) or "index.html")
            return

        self.send_error(404)

    def do_POST(self):
        if self.path == "/upload":
            self._handle_upload()
        else:
            self.send_error(404)

    # -- session-scoped serving -------------------------------------------

    def _serve_session_file(self, session_id, relpath):
        session_dir = os.path.join(self.root_tmp, session_id)

        if relpath.startswith("media/"):
            target = _safe_join(os.path.join(session_dir, "files"), relpath[len("media/"):])
        else:
            target = _safe_join(os.path.join(session_dir, "pages"), relpath)

        if not target:
            self.send_error(404)
            return

        self._send_file(target)

    def _handle_pick_sender(self, session_id, query):
        session = SESSIONS.get(session_id)
        if not session:
            self.send_error(404, "Unknown or expired session — drop the export again.")
            return

        me = (query.get("me") or [None])[0]
        if me:
            show_sender_names = len(session["participants"]) > 2
            pages = generator.generate_chat_pages(
                session["grouped"],
                me=me,
                base_url=f"/chat/{session_id}/",
                output_dir=session["output_dir"],
                show_sender_names=show_sender_names,
            )
            if not pages:
                self._send_text(500, "No messages to display.")
                return
            self._redirect(f"/chat/{session_id}/{pages[0][2]}")
            return

        template = Template((TEMPLATES_DIR / "pick_sender.html").read_text(encoding="utf-8"))
        links = "".join(
            f'<a href="/chat/{session_id}/pick-sender?me={quote(name)}">{html.escape(name)}</a>'
            for name in session["participants"]
        )
        self._send_text(200, template.substitute(participants=links), "text/html; charset=utf-8")

    # -- upload --------------------------------------------------------------

    def _handle_upload(self):
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            self._send_text(400, "Missing upload body.")
            return

        session_id = uuid.uuid4().hex[:12]
        session_dir = os.path.join(self.root_tmp, session_id)
        os.makedirs(session_dir, exist_ok=True)

        zip_path = os.path.join(session_dir, "upload.zip")
        remaining = length
        with open(zip_path, "wb") as f:
            while remaining > 0:
                chunk = self.rfile.read(min(UPLOAD_CHUNK, remaining))
                if not chunk:
                    break
                f.write(chunk)
                remaining -= len(chunk)

        try:
            chat_log_path, attachments = extractor.extract_export(
                zip_path, os.path.join(session_dir, "files")
            )
        except extractor.InvalidExportError as e:
            self._send_text(400, str(e))
            return

        sanitized_path = sanitizer.sanitize_file(chat_log_path)
        messages = textparser.parse_chat_log(sanitized_path, attachments)

        if not messages:
            self._send_text(
                400,
                "This doesn't look like a WhatsApp chat export. Make sure you're "
                "dropping the .zip WhatsApp gave you from Export Chat.",
            )
            return

        missing = [m["attachment_name"] for m in messages if m["attachment_name"] and not m["attachment_path"]]
        if missing:
            sample = ", ".join(sorted(set(missing))[:3])
            print(f"[WhatsText] {len(missing)} attachment(s) referenced in the chat weren't found in the export zip, e.g. {sample}")

        SESSIONS[session_id] = {
            "grouped": textparser.group_messages_by_year_month(messages),
            "files_dir": os.path.join(session_dir, "files"),
            "participants": sorted({m["username"] for m in messages}),
            "output_dir": os.path.join(session_dir, "pages"),
        }

        self._redirect(f"/chat/{session_id}/pick-sender")


def make_handler(root_tmp_dir):
    return type("WhatsTextRequestHandler", (WhatsTextHandler,), {"root_tmp": root_tmp_dir})


def create_server(root_tmp_dir, host="127.0.0.1", port=0):
    return ThreadingHTTPServer((host, port), make_handler(root_tmp_dir))
