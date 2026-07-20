import datetime

from whatstext.textparser import group_messages_by_year_month, parse_chat_log


def _write(tmp_path, content):
    chat_file = tmp_path / "_chat.txt"
    chat_file.write_text(content, encoding="utf-8")
    return str(chat_file)


def test_parse_chat_log_multiple_users(tmp_path):
    path = _write(
        tmp_path,
        "[15/05/23, 10:00:01] Alice: Hello there!\n"
        "[15/05/23, 10:05:00] Bob: Hi Alice! How are you?\n",
    )

    messages = parse_chat_log(path)

    assert len(messages) == 2
    assert messages[0]["username"] == "Alice"
    assert messages[0]["message"] == "Hello there!"
    assert messages[0]["timestamp"] == datetime.datetime(2023, 5, 15, 10, 0, 1)
    assert messages[1]["username"] == "Bob"
    assert messages[1]["message"] == "Hi Alice! How are you?"


def test_parse_chat_log_with_four_digit_year(tmp_path):
    # Regression test: some WhatsApp exports use a 4-digit year (DD/MM/YYYY)
    # instead of 2-digit (DD/MM/YY); the line regex used to require exactly
    # 2 digits, silently dropping every message in these exports.
    path = _write(
        tmp_path,
        "[19/05/2026, 09:03:40] Priya: Okay\n"
        "[19/05/2026, 09:04:12] Arjun: <attached: 00000001-PHOTO-2026-05-21-18-02-11.jpg>\n",
    )

    messages = parse_chat_log(path, attachments={"00000001-PHOTO-2026-05-21-18-02-11.jpg": "/media/x.jpg"})

    assert len(messages) == 2
    assert messages[0]["timestamp"] == datetime.datetime(2026, 5, 19, 9, 3, 40)
    assert messages[1]["attachment_path"] == "/media/x.jpg"


def test_parse_empty_file(tmp_path):
    path = _write(tmp_path, "")
    assert parse_chat_log(path) == []


def test_multiline_message_is_not_duplicated(tmp_path):
    # Regression test: the flush-last-message step used to sit inside the
    # line loop, appending the in-progress message once per continuation line.
    path = _write(
        tmp_path,
        "[15/05/23, 10:00:01] Alice: Line one\nLine two\nLine three\n",
    )

    messages = parse_chat_log(path)

    assert len(messages) == 1
    assert messages[0]["message"] == "Line one\nLine two\nLine three"


def test_attachment_is_resolved_to_extracted_path(tmp_path):
    path = _write(tmp_path, "[15/05/23, 10:00:01] Alice: <attached: IMG-001.jpg>\n")

    messages = parse_chat_log(path, attachments={"IMG-001.jpg": "/media/IMG-001.jpg"})

    assert messages[0]["attachment_name"] == "IMG-001.jpg"
    assert messages[0]["attachment_path"] == "/media/IMG-001.jpg"


def test_attachment_without_extracted_file_resolves_to_none(tmp_path):
    path = _write(tmp_path, "[15/05/23, 10:00:01] Alice: <attached: missing.jpg>\n")

    messages = parse_chat_log(path, attachments={})

    assert messages[0]["attachment_name"] == "missing.jpg"
    assert messages[0]["attachment_path"] is None


def test_group_messages_by_year_month(tmp_path):
    path = _write(
        tmp_path,
        "[15/05/23, 10:00:01] Alice: May message\n"
        "[02/06/23, 09:00:00] Bob: June message\n",
    )

    grouped = group_messages_by_year_month(parse_chat_log(path))

    assert set(grouped[2023].keys()) == {5, 6}
    assert len(grouped[2023][5]) == 1
    assert len(grouped[2023][6]) == 1
