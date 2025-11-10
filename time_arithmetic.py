def time_str_to_seconds(time_str):
    """Convert 'MM:SS' string to total seconds."""
    time_str = str(time_str)
    if not time_str or ':' not in time_str:
        print("DEBUG: no colon found ->", repr(time_str))
        return 0
    minutes, seconds = map(int, time_str.split(':'))
    return minutes * 60 + seconds

def seconds_to_time_str(total_seconds):
    """Convert total seconds to 'MM:SS' string."""
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"

def add_times(time1, time2):
    """Add two 'MM:SS' times together."""
    total_sec = time_str_to_seconds(time1) + time_str_to_seconds(time2)
    return seconds_to_time_str(total_sec)
