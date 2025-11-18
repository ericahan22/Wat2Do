import logging
import os
from datetime import timedelta

from apify_client import ApifyClient
from django.utils import timezone

logger = logging.getLogger(__name__)

class InstagramScraper:
    ACTOR_ID = "apify/instagram-post-scraper"

    def __init__(self, token=None):
        self.token = token or os.getenv("APIFY_API_TOKEN")
        if not self.token:
            logger.critical("APIFY_API_TOKEN not set")
            raise RuntimeError("APIFY_API_TOKEN not set")
        self.client = ApifyClient(self.token)

    def scrape(self, usernames, results_limit=None):
        """
        Run the Apify actor for the given usernames.
        """
        if isinstance(usernames, str):
            usernames = [usernames]

        cutoff_date = timezone.now() - timedelta(days=1)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d")

        run_input = {
            "username": usernames,
            "skipPinnedPosts": True,
            "onlyPostsNewerThan": cutoff_str,
        }
        
        if results_limit:
            run_input["resultsLimit"] = results_limit

        logger.info(f"Starting scrape for {len(usernames)} users (Limit: {results_limit}, Since: {cutoff_str})")
        run = self.client.actor(self.ACTOR_ID).call(run_input=run_input)

        if not run:
            logger.error("Apify run failed or returned no data.")
            return []

        logger.info(f"Scrape finished (Run ID: {run.get('id')}). Fetching results...")
        dataset_items = self.client.dataset(run["defaultDatasetId"]).list_items().items
        logger.info(f"Retrieved {len(dataset_items)} items.")
        
        return dataset_items
