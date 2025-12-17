# Imports
import time
import sys
import os
from pathlib import Path

# External Imports
from rich.console import Console
from rich.theme import Theme

# Submodules
from parser.sanitize import *
from parser.textparser import *
from parser.generator import *
from parser.exporter import *

# Custom theme for consistent styling
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red",
    "success": "bold green"
})

console = Console(theme=custom_theme)

def main():
    if len(sys.argv) < 2:
        console.print("[danger]Error:[/danger] No filepath provided.")
        sys.exit(1)

    filepath = sys.argv[1]
    
    with console.status("[bold blue]Processing chat logs...", spinner="dots") as status:
        
        # Step 1: Sanitize
        console.log(f"Entering [info]sanitize_file[/info] for: {filepath}")
        san_filepath = sanitize_file(filepath)
        time.sleep(0.1) 

        # Step 2: Parse
        status.update("[bold yellow]Parsing chat messages...")
        console.log("Calling [info]parse_chat_log[/info]")
        messages = parse_chat_log(san_filepath)
        console.log(f"Parsed [success]{len(messages)}[/success] messages.")

        # Step 3: Grouping
        status.update("[bold magenta]Grouping messages by date...")
        grouped = group_messages_by_year_month(messages)
        
        # Step 4: HTML Generation
        status.update("[bold green]Generating HTML output...")
        output_dir = os.path.dirname(filepath)
        output_html = os.path.join(output_dir, "chat.html")
        generate_chat_html(grouped, output_html)
        console.log(f"HTML generated at: [link=file://{output_html}]{output_html}[/link]")

        # Step 5: Exporting
        status.update("[bold cyan]Packaging ZIP archive...")
        zip_file = export_chat_package(filepath)
        console.log(f"[success]Exported zip:[/success] {zip_file}")

        # Step 6: Cleanup
        status.update("[dim]Cleaning up temporary files...")
        if os.path.exists(output_html):
            os.remove(output_html)

        sanitized_file = os.path.join(os.path.dirname(filepath), "_chat_sanitized.txt")
        if os.path.exists(sanitized_file):
            os.remove(sanitized_file)

    console.print("\n[bold success]✨ Chats Beautified Successfully! ✨[/bold success]")

if __name__ == "__main__":
    console.log("[grey50]__main__ block executing[/grey50]")
    main()