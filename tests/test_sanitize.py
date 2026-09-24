import os

from whatstext.sanitizer import sanitize_file, sanitize_text


def test_sanitize_text_strips_control_chars_and_trailing_whitespace():
    assert sanitize_text("Hello\x00World \n") == "HelloWorld\n"


def test_sanitize_text_normalizes_crlf():
    assert sanitize_text("line1\r\nline2\r\nline3") == "line1\nline2\nline3"


def test_sanitize_text_nfkc_normalizes_unicode():
    assert sanitize_text("ＡＢ") == "AB"


def test_sanitize_text_preserves_newlines_and_tabs():
    assert sanitize_text("a\n\tb") == "a\n\tb"


def test_sanitize_text_does_not_censor_profanity():
    # Profanity filtering is applied per-message at render time (generator.py),
    # toggleable in the UI - sanitize_text must leave message text untouched so
    # the original is still available when the toggle is off.
    assert sanitize_text("this is a damn test") == "this is a damn test"


def test_sanitize_file_writes_sanitized_copy(tmp_path):
    src = tmp_path / "_chat.txt"
    src.write_text("Hello\x00World \n", encoding="utf-8")

    out_path = sanitize_file(str(src))

    assert out_path.endswith("_chat_sanitized.txt")
    assert os.path.exists(out_path)
    with open(out_path, encoding="utf-8") as f:
        assert f.read() == "HelloWorld\n"
