def determine_display_handle(event):
    """
    Determine a display handle for an event.
    Accepts either a dict-like object (with .get) or a Django model instance (attributes).
    Prefers social handles in order: ig, discord, x, tiktok, fb. Prepends '@' unless already present.
    Falls back to event.school or "Wat2Do Event".
    """

    def _get(key):
        # dict
        if hasattr(event, "get"):
            return event.get(key)
        # model instance / object
        return getattr(event, key, None)

    social_handles = [
        _get("ig_handle"),
        _get("discord_handle"),
        _get("x_handle"),
        _get("tiktok_handle"),
        _get("fb_handle"),
    ]
    social_handles = [h for h in social_handles if h]

    if social_handles:
        handle = social_handles[0]
        handle_str = str(handle)
        return handle_str
    school = _get("school")
    return school or "Wat2Do Event"
