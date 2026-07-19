import re
import datetime
from collections import defaultdict

CHAT_LINE_RE = re.compile(r'\[(\d{2}/\d{2}/\d{2}), (\d{2}:\d{2}:\d{2})\] (.*?): (.*)')
MEDIA_RE = re.compile(r'<attached:\s*(.*?)>')


def parse_chat_log(file_path, attachments=None):
    """
    Parse text file into structured message objects using regex.

    Args:
        file_path (str): Path to the sanitized chat log.
        attachments (dict[str, str] | None): filename -> extracted file path,
            used to resolve "<attached: X>" references to real files on disk.

    Returns:
        List[Dict]: message dicts with 'timestamp', 'username', 'message',
        'attachment_name' and 'attachment_path' (the latter two None when
        the message has no attachment).
    """
    attachments = attachments or {}

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    messages = []
    current = None

    for raw_line in lines:
        log_match = CHAT_LINE_RE.match(raw_line)

        if log_match:
            if current:
                messages.append(current)

            date_str, time_str, username, message = log_match.groups()
            timestamp = datetime.datetime.strptime(
                f"{date_str} {time_str}", "%d/%m/%y %H:%M:%S"
            )
            message = message.strip()

            current = {
                "timestamp": timestamp,
                "username": username,
                "message": message,
                "attachment_name": None,
                "attachment_path": None,
            }

            media_match = MEDIA_RE.search(message)
            if media_match:
                name = media_match.group(1).strip()
                current["attachment_name"] = name
                current["attachment_path"] = attachments.get(name)
            continue

        if not current:
            continue

        # continuation of previous message (multiline)
        current["message"] += "\n" + raw_line.strip()

    if current:
        messages.append(current)

    return messages


def group_messages_by_year_month(messages):
    """
    Organize flat list of messages into nested year/month hierarchy.

    Args:
        messages (List[Dict]): List of message dictionaries.

    Returns:
        Dict: Nested dictionary formatted as {year: {month: [messages]}}.
    """
    grouped = defaultdict(lambda: defaultdict(list))

    for msg in messages:
        ts = msg["timestamp"]
        grouped[ts.year][ts.month].append(msg)

    return grouped
