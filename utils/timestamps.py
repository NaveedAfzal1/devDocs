from datetime import datetime, timezone

def add_timestamps(data: dict, is_update: bool = False) -> dict:
    """
    6. Add Automatic Timestamps
    - For new documents, adds `created_at` and `updated_at`.
    - For updates, only updates `updated_at`.
    """
    now = datetime.now(timezone.utc).isoformat()
    if is_update:
        data["updated_at"] = now
    else:
        data["created_at"] = now
        data["updated_at"] = now
    return data