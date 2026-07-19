import os
import re
import zipfile

CHAT_LOG_RE = re.compile(r"_?chat\.txt$", re.IGNORECASE)


class InvalidExportError(Exception):
    pass


def extract_export(zip_path, target_dir):
    """
    Extracts a WhatsApp export zip to target_dir, streaming each member to disk.

    zipfile.extract() has sanitized '..'/absolute path components since
    Python 3.6.4, so members can't be written outside target_dir.

    Args:
        zip_path (str): Path to the uploaded .zip file.
        target_dir (str): Directory to extract into.

    Returns:
        tuple[str, dict[str, str]]: path to the chat log file, and a dict
        mapping attachment filename -> extracted absolute path.
    """
    os.makedirs(target_dir, exist_ok=True)
    chat_log_path = None
    attachments = {}

    try:
        zf = zipfile.ZipFile(zip_path)
    except zipfile.BadZipFile:
        raise InvalidExportError("That file isn't a valid .zip archive.")

    with zf:
        for member in zf.infolist():
            if member.is_dir():
                continue

            dest_path = zf.extract(member, target_dir)
            filename = os.path.basename(dest_path)

            if CHAT_LOG_RE.search(filename):
                chat_log_path = dest_path
            else:
                attachments[filename] = dest_path

    if chat_log_path is None:
        txt_files = [f for f in attachments if f.lower().endswith(".txt")]
        if len(txt_files) == 1:
            chat_log_path = attachments.pop(txt_files[0])

    if chat_log_path is None:
        raise InvalidExportError(
            "No chat log (_chat.txt) found in this zip. "
            "Make sure you're dropping the WhatsApp export .zip."
        )

    return chat_log_path, attachments
