import logging
import os
from datetime import timedelta

from apify_client import ApifyClient
from apify_client.errors import ApifyApiError
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

    def scrape(self, usernames, results_limit=None, cutoff_days=1):
        """
        Run the Apify actor for the given usernames.
        Args:
            usernames: Instagram username(s) to scrape
            results_limit: Maximum number of posts to retrieve per user
            cutoff_days: Number of days to look back for posts (default: 1)
        """
        if isinstance(usernames, str):
            usernames = [usernames]

        cutoff_date = timezone.now() - timedelta(days=cutoff_days)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d")

        run_input = {
            "username": usernames,
            "skipPinnedPosts": True,
            "onlyPostsNewerThan": cutoff_str,
        }

        if results_limit:
            run_input["resultsLimit"] = results_limit

        logger.info(
            f"Starting scrape for {len(usernames)} users (Limit: {results_limit}, Since: {cutoff_str})"
        )
        try:
            run = self.client.actor(self.ACTOR_ID).start(
                run_input=run_input,
            )

            # Poll for completion
            import time

            run_id = run["id"]
            logger.info(f"Scrape started (Run ID: {run_id}). Waiting for completion...")

            start_time = time.time()
            timeout_secs = 600  # 10 minutes

            while True:
                if time.time() - start_time > timeout_secs:
                    logger.error(f"Scrape timed out after {timeout_secs} seconds")
                    self.client.run(run_id).abort()
                    return []

                run = self.client.run(run_id).get()
                status = run.get("status")
                if status in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
                    break
                time.sleep(5)

            if status != "SUCCEEDED":
                logger.error(f"Apify run failed with status: {status}")
                return []

        except ApifyApiError as e:
            logger.error(f"Apify API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Apify actor call failed: {e}")
            return []

        logger.info(f"Scrape finished (Run ID: {run.get('id')}). Fetching results...")
        try:
            dataset_items = (
                self.client.dataset(run["defaultDatasetId"]).list_items().items
            )
            logger.info(f"Retrieved {len(dataset_items)} items.")
        except Exception as e:
            logger.error(f"Failed to fetch dataset items: {e}")
            return []

        return dataset_items
