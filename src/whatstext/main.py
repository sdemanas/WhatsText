# Imports
from pyexpat.errors import messages
import time
import sys
import os

# Submodules
from sanitizer import sanitize_file
from textparser import parse_chat_log, group_messages_by_year_month
from generator import generate_chat_html
from exporter import export_chat_package

def spinner_wait(message, seconds):
    """
    Displays a spinning animation for a set duration.
    
    Args: 
        message (str): Task description, seconds (int): Duration.
    Returns: 
        None
    """
    chars = ["|", "/", "-", "\\"]
    end_time = time.time() + seconds
    i = 0
    while time.time() < end_time:
        sys.stdout.write(f"\r{chars[i % len(chars)]} {message}...")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write(f"\r[OK] {message} complete.    \n")

def main():
    if len(sys.argv) < 2:
        print("[Error] No filepath provided. Usage: python main.py <file_path>")
        return

    filepath = sys.argv[1]
    output_dir = os.path.dirname(os.path.abspath(filepath))
    page_size = int(sys.argv[2]) if len(sys.argv) > 2 else 100

    print(f"\n--- ✨ WhatsText is Processing: {os.path.basename(filepath)} ✨ ---\n")

    # Loading animation time
    animation_time = 1.0

    # Step 1: Sanitize
    spinner_wait("Sanitizing chat logs", animation_time)
    san_filepath = sanitize_file(filepath)

    # Step 2: Parse
    spinner_wait("Parsing message structures", animation_time)
    messages = parse_chat_log(san_filepath)
    print(f"[*] Indexed {len(messages)} messages.")

    # Step 3: Grouping
    spinner_wait("Organizing by Year/Month", animation_time)
    grouped = group_messages_by_year_month(messages)

    # Step 4: HTML Generation
    spinner_wait("Generating HTML view", animation_time)
    total_messages = len(messages)  # Use flat messages for even pagination
    total_pages = (total_messages + page_size - 1) // page_size
    print(f"[*] Generating {total_pages} paginated HTML pages (size={page_size}).")

    for page_num in range(1, total_pages + 1):
        start_idx = (page_num - 1) * page_size
        page_messages = messages[start_idx : start_idx + page_size]
        page_grouped = group_messages_by_year_month(page_messages)  # Regroup page subset
        output_html = os.path.join(output_dir, f"chat_page_{page_num}.html")
        generate_chat_html(page_grouped, output_html, page_size, total_pages, total_messages, page_num)

    # Step 5: Exporting
    spinner_wait("Packaging for export", animation_time)
    zip_file = export_chat_package(filepath, "chat_page_")
    print(f"[*] Exported zip: {zip_file}")

    # Step 6: Cleanup
    spinner_wait("Cleaning intermediate files", animation_time)
    for page_num in range(1, 1000):  # Arbitrary large number to include all pages
        page_file = f"chat_page_{page_num}.html"
        page_path = os.path.join(output_dir, page_file)
        print(f"Cleaning: {page_path}")
        if os.path.exists(page_path):
            os.remove(page_path)
        else:
            break
    
    # Clean up the specific sanitized file created in Step 1
    if os.path.exists(san_filepath):
        os.remove(san_filepath)

    print("\n[SUCCESS] Beautified zip ready in directory. 🗂️ \n")

if __name__ == "__main__":
    main()