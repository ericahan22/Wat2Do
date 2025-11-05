import re
from difflib import SequenceMatcher
from scraping.logging_config import logger


def normalize(s):
    """Normalize a string for comparison (lowercase, alphanumeric only)."""
    return re.sub(r"[^a-z0-9]", "", s.lower())


def jaccard_similarity(a, b):
    """Compute Jaccard similarity between two strings (case-insensitive, word-based)."""
    set_a = set(re.findall(r"\w+", a.lower()))
    set_b = set(re.findall(r"\w+", b.lower()))
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)


def sequence_similarity(a, b):
    """Compute SequenceMatcher similarity between two strings (case-insensitive)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def get_post_image_url(post):
    try:
        if post._node.get("image_versions2"):
            return post._node["image_versions2"]["candidates"][0]["url"]
        if post._node.get("carousel_media"):
            return post._node["carousel_media"][0]["image_versions2"]["candidates"][0]["url"]
        if post._node.get("display_url"):
            return post._node["display_url"]
        return None
    except (KeyError, AttributeError) as e:
        logger.warning(f"Failed to extract image URL from post: {e}")
        return None
