
def timestamp_to_elapsed_string(timestamp):
    import time
    elapsed = int(time.time() - timestamp)
    if elapsed < 60:
        return "a few seconds ago"
    elif elapsed < 3600:
        return f"{elapsed // 60} minutes ago"
    elif elapsed < 86400:
        return f"{elapsed // 3600} hours ago"
    return f"{elapsed // 86400} days ago"
