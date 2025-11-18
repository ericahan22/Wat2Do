import os
import logging
from datetime import timedelta
from django.utils import timezone
from apify_client import ApifyClient

logger = logging.getLogger(__name__)

APIFY_TOKEN = os.getenv("APIFY_API_TOKEN")
APIFY_ACTOR = "apify/instagram-post-scraper"

def run_apify_scraper(usernames=None, results_limit=None):
    """
    Run Apify actor for one or more usernames and return the results.
    """
    if not APIFY_TOKEN:
        logger.critical("APIFY_API_TOKEN not set")
        raise RuntimeError("APIFY_API_TOKEN not set")

    cutoff_date = timezone.now() - timedelta(days=1)
    cutoff_str = cutoff_date.strftime("%Y-%m-%d")

    client = ApifyClient(APIFY_TOKEN)

    input_data = {
        "skipPinnedPosts": True,
        "onlyPostsNewerThan": cutoff_str,
    }

    if usernames:
        if isinstance(usernames, str):
            usernames = [usernames]
        input_data["username"] = usernames
    
    if results_limit is not None:
        input_data["resultsLimit"] = results_limit

    logger.info(f"Starting Apify actor with cutoff {cutoff_str} for: {usernames}")

    run = client.actor(APIFY_ACTOR).call(run_input=input_data)

    if not run:
        logger.error("Apify run failed or returned no data.")
        return []

    logger.info(f"Apify run finished (ID: {run.get('id')}). Fetching dataset...")
    dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items
    
    logger.info(f"Retrieved {len(dataset_items)} items from Apify.")
    return dataset_items
