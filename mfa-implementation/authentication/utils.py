

def current_local_time():
    """Current time of day in the project's timezone."""
    now = timezone.now()
    if timezone.is_aware(now):
        now = timezone.localtime(now)
    return now.time()


def is_within_shift(start, end, now):
    """True if `now` falls inside the shift window. Handles overnight shifts."""
    if start <= end:
        return start <= now <= end
    return now >= start or now <= end

