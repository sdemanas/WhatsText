import re
import datetime
from collections import defaultdict
from typing import Dict, List

def parse_chat_log(file_path):
    """
    Parses a text file into structured message objects using regex.

    Args: 
        file_path (str): Path to the sanitized chat log.

    Returns: 
        List[Dict]: List of dicts containing 'timestamp', 'username', and 'message'.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    messages = []
    
    log_pattern = r'\[(\d{2}/\d{2}/\d{2}), (\d{2}:\d{2}:\d{2})\] (.*?): (.*)'
    # attachment_pattern = r'<attached:\s*(.*?)>'
    # filename_ts_pattern = r'(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})'
    
    current = None

    for raw_line in lines:
        log_match = re.match(log_pattern, raw_line)

        if log_match:
            if current:
                messages.append(current)

            date_str, time_str, username, message = log_match.groups()
            timestamp = datetime.datetime.strptime(
                f"{date_str} {time_str}", "%d/%m/%y %H:%M:%S"
            )

            current = {
                "timestamp": timestamp,
                "username": username,
                "message": message.strip()
            }
            continue

        if not current:
            continue
        # continuation of previous message (multiline)
        current["message"] += "\n" + raw_line.strip()

    # flush last message
    if current:
        messages.append(current)

    # To-Do : attachment handling 
    return messages

def group_messages_by_year_month(messages):
    """
    Organizes a flat list of messages into a nested year/month hierarchy.

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
