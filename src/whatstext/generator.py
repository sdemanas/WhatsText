import calendar
from pathlib import Path
from string import Template
import html

BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATE_PATH = BASE_DIR / "whatstext" / "assets" / "templates" / "chat_view.html"
STATIC_PATH = BASE_DIR / "whatstext" / "assets" / "static"

def generate_chat_html(grouped_messages, output_path):
    """
    Generates html file within the _chat.txt directory
    
    Args: 
       grouped_messages (object): dictionary object of grouped messages
       output_path (str): output path of the argument passed _chat.txt

    Returns: 
        null
    """
    template = Template(TEMPLATE_PATH.read_text(encoding="utf-8"))

    users = set()
    for y in grouped_messages.values():
        for m in y.values():
            for msg in m:
                users.add(msg["username"])

    users = list(users)
    user_colors = {
        users[0]: "user-a",
        users[1]: "user-b"
    } if len(users) == 2 else {}

    body = []

    for year in sorted(grouped_messages):
        for month_num in sorted(grouped_messages[year]):
            month_name = calendar.month_name[month_num] 
            body.append(f'<div class="month">{month_name} {year}</div>')

            for msg in grouped_messages[year][month_num]:
                username = html.escape(msg["username"])
                text = html.escape(msg["message"]).replace("\n", "<br>")
                time = msg["timestamp"].strftime("%H:%M:%S")
                cls = user_colors.get(msg["username"], "user-default")

                body.append(f"""
                <div class="message {cls}">
                    <div class="meta">
                        <span class="user">{username}</span>
                        <span class="time">{time}</span>
                    </div>
                    <div class="text">{text}</div>
                </div>
                """)

    html_out = template.substitute(content="\n".join(body))

    Path(output_path).write_text(html_out, encoding="utf-8")