from whatstext.generator import _render_text, generate_chat_pages
from whatstext.textparser import group_messages_by_year_month
import datetime


def test_render_text_clean_message_still_has_both_divs():
    # Regression test: the toggle CSS unconditionally hides .text-original
    # when the filter is on and shows .text-censored - a clean message
    # missing the .text-censored div would render blank in that state.
    html_out = _render_text("this is a clean message")

    assert 'class="text text-original"' in html_out
    assert 'class="text text-censored"' in html_out
    assert html_out.count("clean message") == 2


def test_render_text_profane_message_has_both_divs():
    html_out = _render_text("this is a damn test")

    assert 'class="text text-original"' in html_out
    assert 'class="text text-censored"' in html_out
    assert "this is a damn test" in html_out  # original, uncensored
    assert "this is a **** test" in html_out  # censored


def _message(username, text, ts=datetime.datetime(2023, 5, 15, 10, 0, 0)):
    return {
        "timestamp": ts,
        "username": username,
        "message": text,
        "attachment_name": None,
        "attachment_path": None,
    }


def test_generated_page_includes_profanity_toggle_and_both_text_variants(tmp_path):
    messages = [_message("Alice", "this is a damn test")]
    grouped = group_messages_by_year_month(messages)

    pages = generate_chat_pages(
        grouped, me="Alice", base_url="/chat/test/", output_dir=str(tmp_path)
    )

    page_html = (tmp_path / pages[0][2]).read_text(encoding="utf-8")

    assert 'id="profanity-toggle"' in page_html
    assert "this is a damn test" in page_html
    assert "this is a **** test" in page_html


def test_generated_page_clean_message_still_visible_with_filter_on(tmp_path):
    # A clean message must still render its text when the toggle is switched
    # on client-side - it needs a .text-censored div to show, even though
    # the content is identical to .text-original.
    messages = [_message("Alice", "hello there, all good")]
    grouped = group_messages_by_year_month(messages)

    pages = generate_chat_pages(
        grouped, me="Alice", base_url="/chat/test/", output_dir=str(tmp_path)
    )

    page_html = (tmp_path / pages[0][2]).read_text(encoding="utf-8")

    assert 'class="text text-censored"' in page_html
    assert page_html.count("hello there, all good") == 2
