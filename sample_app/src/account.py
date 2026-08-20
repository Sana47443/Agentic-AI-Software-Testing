def normalize_email(email: str) -> str:
    return email.strip().lower()

def can_reset_password(email: str) -> bool:
    return "@" in normalize_email(email)

def reset_message(email: str) -> str:
    if not can_reset_password(email):
        return "invalid"
    return "reset-link-requested"

def internal_audit_label(email: str) -> str:
    return f"audit:{normalize_email(email)}"
