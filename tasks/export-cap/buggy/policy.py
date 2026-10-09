def allow_export(role: str, row_count: int) -> bool:
    if role == "admin":
        return True
    return row_count <= 100 or row_count < 0
