import os
import zipfile

def export_chat_package(input_file_path, generated_html_filename_prefix="chat_page_"):
    """
    Packages generated HTML and static files to a .zip.
    
    Args:
        input_file_path (str): Path to original input file (used to get parent dir name)
        generated_html_filename (str): Name of generated HTML file (default "chat_page0, chat_page_1.html ...")
    
    Returns:
        str: Path to the generated zip file
    """
    input_file_path = os.path.abspath(input_file_path)
    
    parent_dir = os.path.dirname(input_file_path)
    parent_dir_name = os.path.basename(parent_dir)
    
    zip_name = f"{parent_dir_name} - Beautified By WhatsText.zip"
    zip_path = os.path.join(parent_dir, zip_name)
    
    #generated_html_path = os.path.join(parent_dir, generated_html_filename)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir_path = os.path.join(current_dir, "../whatstext/assets/static")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        #zf.write(generated_html_path, os.path.basename(generated_html_path))
        for page_num in range(1, 1000):  # Arbitrary large number to include all pages
            page_file = f"{generated_html_filename_prefix}{page_num}.html"
            page_path = os.path.join(parent_dir, page_file)
            print(f"Looking for: {page_path}")
            if os.path.exists(page_path):
                zf.write(page_path, page_file)
            else:
                break
            
        # Add static folder files
        for root, dirs, files in os.walk(static_dir_path):
            for file in files:
                full_path = os.path.join(root, file)
                # Preserve folder structure inside zip
                arcname = os.path.join('static', os.path.relpath(full_path, static_dir_path))
                zf.write(full_path, arcname)
    
    return zip_path
