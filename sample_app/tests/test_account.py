from sample_app.src.account import normalize_email, can_reset_password, reset_message

def test_normalize_email():
    assert normalize_email(" USER@example.com ") == "user@example.com"

def test_can_reset_password():
    assert can_reset_password("user@example.com")
    assert not can_reset_password("invalid")

def test_reset_message():
    assert reset_message("user@example.com") == "reset-link-requested"
