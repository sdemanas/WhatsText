# Imports
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
    output_html = os.path.join(output_dir, "chat.html")
    generate_chat_html(grouped, output_html)

    # Step 5: Exporting
    spinner_wait("Packaging for export", animation_time)
    zip_file = export_chat_package(filepath)
    print(f"[*] Exported zip: {zip_file}")

    # Step 6: Cleanup
    spinner_wait("Cleaning intermediate files", animation_time)
    if os.path.exists(output_html):
        os.remove(output_html)
    
    # Clean up the specific sanitized file created in Step 1
    if os.path.exists(san_filepath):
        os.remove(san_filepath)

    print("\n[SUCCESS] Beautified zip ready in directory. 🗂️ \n")

if __name__ == "__main__":
    main()