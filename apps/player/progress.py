from .models import WatchProgress

CONTINUE_LIMIT = 12
FINISHED_PERCENT = 95


def continue_watching(user) -> list[WatchProgress]:
    """Latest unfinished progress per title, newest first. Logged-in users only."""
    if not user.is_authenticated:
        return []
    recent = (
        WatchProgress.objects.filter(user=user)
        .select_related("episode__season__movie")
        .order_by("-updated_at")[: CONTINUE_LIMIT * 3]
    )
    seen: set[int] = set()
    items = []
    for progress in recent:
        movie_id = progress.episode.season.movie_id
        if movie_id in seen:
            continue
        seen.add(movie_id)
        if progress.percent < FINISHED_PERCENT:
            items.append(progress)
    return items[:CONTINUE_LIMIT]
