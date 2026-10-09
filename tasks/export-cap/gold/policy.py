def allow_export(role: str, row_count: int) -> bool:
    if role == "admin":
        return True
    return 0 <= row_count <= 100
