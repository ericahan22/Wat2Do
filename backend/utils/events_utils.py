def determine_display_handle(event):
    """
    Determine a display handle for an event.
    Accepts either a dict-like object (with .get) or a Django model instance (attributes).
    Prefers ig_handle, then other_handle, then event.school.
    """

    def _get(key):
        # dict
        if hasattr(event, "get"):
            return event.get(key)
        # model instance / object
        return getattr(event, key, None)

    ig_handle = _get("ig_handle")
    other_handle = _get("other_handle")
    school = _get("school")

    if ig_handle:
        return str(ig_handle)
    if other_handle:
        return str(other_handle)
    return school or "Wat2Do Event"
