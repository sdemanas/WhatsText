import calendar
import html
import os
from pathlib import Path
from string import Template
from urllib.parse import quote

from better_profanity import profanity

from .textparser import MEDIA_RE

profanity.load_censor_words()

PACKAGE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = PACKAGE_DIR / "assets" / "templates" / "chat_view.html"

STATIC_PREFIX = "/static"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".3gp", ".webm"}
AUDIO_EXTS = {".opus", ".mp3", ".m4a", ".ogg", ".wav"}
LARGE_IMAGE_BYTES = 20 * 1024 * 1024


def _render_attachment(msg, media_base_url):
    path = msg["attachment_path"]
    name = msg["attachment_name"]
    if not path or not os.path.exists(path):
        return f'<div class="attachment-missing">📎 {html.escape(name or "attachment")} (not found)</div>'

    url = media_base_url + quote(os.path.basename(path))
    ext = os.path.splitext(path)[1].lower()
    size = os.path.getsize(path)
    safe_name = html.escape(name)

    if ext in IMAGE_EXTS:
        if size > LARGE_IMAGE_BYTES:
            return (
                f'<a class="attachment-large" href="{url}" target="_blank" rel="noopener">'
                f"🖼️ {safe_name} ({size // (1024 * 1024)} MB — click to view)</a>"
            )
        return f'<a href="{url}" target="_blank" rel="noopener"><img src="{url}" loading="lazy" class="attachment-image" alt="{safe_name}"></a>'

    if ext in VIDEO_EXTS:
        return f'<video controls preload="none" class="attachment-video"><source src="{url}"></video>'

    if ext in AUDIO_EXTS:
        return f'<audio controls preload="none" class="attachment-audio" src="{url}"></audio>'

    return f'<a class="attachment-file" href="{url}" download>📎 {safe_name}</a>'


def _render_message(msg, me, media_base_url, show_sender_name):
    username = html.escape(msg["username"])
    text = _strip_media_tag(msg["message"])
    time = msg["timestamp"].strftime("%H:%M")
    sent = msg["username"] == me
    cls = "sent" if sent else "received"

    parts = [f'<div class="bubble">']
    if show_sender_name and not sent:
        parts.append(f'<div class="sender">{username}</div>')
    if msg["attachment_name"]:
        parts.append(_render_attachment(msg, media_base_url))
    if text:
        parts.append(_render_text(text))
    parts.append(f'<div class="time">{time}</div>')
    parts.append("</div>")

    return f'<div class="message {cls}">' + "".join(parts) + "</div>"


def _strip_media_tag(text):
    return MEDIA_RE.sub("", text).strip()


def _render_text(text):
    original = html.escape(text).replace(chr(10), "<br>")
    censored_text = profanity.censor(text, "*")

    if censored_text == text:
        return f'<div class="text text-original">{original}</div>'

    censored = html.escape(censored_text).replace(chr(10), "<br>")
    return (
        f'<div class="text text-original">{original}</div>'
        f'<div class="text text-censored">{censored}</div>'
    )


def _render_day_messages(day, messages, me, media_base_url, show_sender_name):
    out = [f'<div class="day-divider"><span>{day.strftime("%d %B %Y")}</span></div>']
    for msg in messages:
        out.append(_render_message(msg, me, media_base_url, show_sender_name))
    return "".join(out)


def generate_chat_pages(grouped_messages, me, base_url, output_dir, show_sender_names=False):
    """
    Generates one HTML page per year/month with prev/next navigation, plus
    an index.html that redirects to the earliest month.

    Args:
        grouped_messages (dict): {year: {month: [messages]}}
        me (str): username to right-align/highlight as the local sender.
        base_url (str): absolute URL prefix for this session, e.g. "/chat/<id>/".
        output_dir (str): directory to write the generated HTML pages into.
        show_sender_names (bool): show sender name above received bubbles
            (group chats); off for 1:1 chats.

    Returns:
        list[tuple[int, int, str]]: (year, month, filename) in chronological order.
    """
    os.makedirs(output_dir, exist_ok=True)
    template = Template(TEMPLATE_PATH.read_text(encoding="utf-8"))
    media_base_url = base_url + "media/"

    pages = []
    for year in sorted(grouped_messages):
        for month in sorted(grouped_messages[year]):
            pages.append((year, month))

    filenames = {(y, m): f"{y:04d}-{m:02d}.html" for y, m in pages}

    for i, (year, month) in enumerate(pages):
        messages = grouped_messages[year][month]

        by_day = {}
        for msg in messages:
            day = msg["timestamp"].date()
            by_day.setdefault(day, []).append(msg)

        body = "".join(
            _render_day_messages(day, by_day[day], me, media_base_url, show_sender_names)
            for day in sorted(by_day)
        )

        month_label = f"{calendar.month_name[month]} {year}"

        prev_link = ""
        if i > 0:
            prev_url = base_url + filenames[pages[i - 1]]
            prev_link = f'<a href="{prev_url}">&larr; {calendar.month_name[pages[i - 1][1]]} {pages[i - 1][0]}</a>'

        next_link = ""
        if i < len(pages) - 1:
            next_url = base_url + filenames[pages[i + 1]]
            next_link = f'<a href="{next_url}">{calendar.month_name[pages[i + 1][1]]} {pages[i + 1][0]} &rarr;</a>'

        page_html = template.substitute(
            month_label=html.escape(month_label),
            content=body,
            prev_link=prev_link,
            next_link=next_link,
            static_prefix=STATIC_PREFIX,
        )

        Path(output_dir, filenames[(year, month)]).write_text(page_html, encoding="utf-8")

    if pages:
        first_page = filenames[pages[0]]
        redirect_html = (
            f'<!DOCTYPE html><meta charset="utf-8">'
            f'<meta http-equiv="refresh" content="0; url={base_url}{first_page}">'
        )
        Path(output_dir, "index.html").write_text(redirect_html, encoding="utf-8")

    return [(y, m, filenames[(y, m)]) for y, m in pages]
