"""
Script to validate event source URLs and remove events with invalid/deleted sources.
Checks if Instagram posts and other event sources are still accessible.
Uses async/concurrent requests for fast validation.
"""

import asyncio
import os
import random
import re
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

import aiohttp
from django.db import connection, transaction

from apps.events.models import (
    EventDates,
    EventInterest,
    Events,
    EventSubmission,
)
from scraping.logging_config import logger


class EventSourceValidator:
    """Validates event source URLs and removes invalid events"""

    def __init__(self, max_concurrent=2, delay_between_requests=1.0):
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.max_concurrent = max_concurrent
        self.delay_between_requests = delay_between_requests

        # Track statistics
        self.stats = {
            "total_checked": 0,
            "valid": 0,
            "invalid": 0,
            "deleted_events": 0,
            "deleted_event_dates": 0,
            "errors": 0,
            "rate_limited": 0,
        }

        # Track events to delete (populated during async validation)
        self.events_to_delete = []

    def is_instagram_url(self, url):
        """Check if URL is an Instagram post"""
        if not url:
            return False
        return bool(
            re.search(r"instagram\.com/p/|instagram\.com/reel/", url, re.IGNORECASE)
        )

    async def check_instagram_post(self, session, url):
        """
        Check if an Instagram post is still available.
        Returns: (is_valid: bool | None, reason: str)
        - True: Post is valid
        - False: Post is definitely invalid (404, unavailable message)
        - None: Indeterminate (rate-limited, timeout, error) - do not delete
        """
        try:
            logger.info(f"Checking Instagram URL: {url}")

            if self.delay_between_requests > 0:
                jitter = random.uniform(0.5, 2.0)
                await asyncio.sleep(self.delay_between_requests + jitter)

            # Try to access the post
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=10), allow_redirects=True
            ) as response:
                content = await response.read()
                final_url = str(response.url)

                # Instagram returns 404 for deleted posts
                if response.status == 404:
                    logger.warning(f"Instagram post not found (404): {url}")
                    return False, "404 Not Found"

                # Check for rate-limiting (redirected to login/error page)
                if "login" in final_url.lower() or "error" in final_url.lower():
                    logger.warning(
                        f"Instagram rate-limiting detected (login redirect): {url}. Backing off for 60s..."
                    )
                    self.stats["rate_limited"] += 1
                    await asyncio.sleep(60)
                    return None, "Rate-limited (login redirect)"

                # Check page content for Instagram's error messages
                if (
                    b"Post isn't available" in content
                    or b"post isn't available" in content
                    or b"The link may be broken" in content
                    or b"profile may have been removed" in content
                    or b"Sorry, this page isn't available" in content
                    or b"The link you followed may be broken" in content
                ):
                    logger.warning(
                        f"Instagram post page shows unavailable message: {url}"
                    )
                    return False, "Page unavailable message"

                # Check for "Page Not Found"
                if b"Page Not Found" in content:
                    logger.warning(f"Instagram post shows Page Not Found: {url}")
                    return False, "Page Not Found"

                # If we get here with 200, the post exists
                if response.status == 200:
                    logger.info(f"Instagram post is valid: {url}")
                    return True, "Valid"

                # Other status codes
                logger.warning(
                    f"Instagram post returned status {response.status}: {url}"
                )
                return None, f"HTTP {response.status} (indeterminate)"

        except asyncio.TimeoutError:
            logger.error(f"Timeout checking Instagram URL: {url}")
            return None, "Timeout"  # None means indeterminate, don't delete

        except Exception as e:
            logger.error(f"Error checking Instagram URL {url}: {e}")
            return None, f"Request error: {e!s}"

    async def check_generic_url(self, session, url):
        """
        Check if a generic URL is still accessible.
        Returns: (is_valid: bool, reason: str)
        """
        try:
            logger.info(f"Checking generic URL: {url}")

            async with session.head(
                url, timeout=aiohttp.ClientTimeout(total=10), allow_redirects=True
            ) as response:
                # Consider 200-399 as valid
                if 200 <= response.status < 400:
                    logger.info(f"URL is valid: {url}")
                    return True, "Valid"

                # 404 means not found - delete
                if response.status == 404:
                    logger.warning(f"URL not found (404): {url}")
                    return False, "404 Not Found"

                # 410 Gone means permanently removed - delete
                if response.status == 410:
                    logger.warning(f"URL gone (410): {url}")
                    return False, "410 Gone"

                # Other 4xx or 5xx - consider invalid
                if response.status >= 400:
                    logger.warning(
                        f"URL returned error status {response.status}: {url}"
                    )
                    return False, f"HTTP {response.status}"

                return True, "Valid"

        except asyncio.TimeoutError:
            logger.error(f"Timeout checking URL: {url}")
            return None, "Timeout"

        except Exception as e:
            logger.error(f"Error checking URL {url}: {e}")
            return None, f"Request error: {e!s}"

    async def check_event_source(self, session, event):
        """
        Check if an event's source URL is still valid.
        Returns: (is_valid: bool, reason: str, event: Event)
        """
        if not event.source_url:
            logger.debug(f"Event {event.id} has no source URL, skipping")
            return True, "No source URL", event

        self.stats["total_checked"] += 1

        # Check Instagram posts differently
        if self.is_instagram_url(event.source_url):
            is_valid, reason = await self.check_instagram_post(
                session, event.source_url
            )
        else:
            is_valid, reason = await self.check_generic_url(session, event.source_url)

        # Update stats
        if is_valid is True:
            self.stats["valid"] += 1
        elif is_valid is False:
            self.stats["invalid"] += 1
        else:
            self.stats["errors"] += 1

        return is_valid, reason, event

    def delete_event(self, event, reason):
        """Delete an event and all its related data"""
        try:
            # Close existing database connections to prevent SSL SYSCALL errors
            connection.close()

            with transaction.atomic():
                event_id = event.id
                event_title = event.title or "Untitled"

                # Count related objects before deletion
                event_dates_count = EventDates.objects.filter(event=event).count()
                interests_count = EventInterest.objects.filter(event=event).count()
                submissions_count = EventSubmission.objects.filter(
                    created_event=event
                ).count()

                logger.info(
                    f"Deleting event {event_id}: '{event_title[:50]}' | "
                    f"Reason: {reason} | "
                    f"URL: {event.source_url} | "
                    f"Related: {event_dates_count} dates, {interests_count} interests, {submissions_count} submissions"
                )

                # Django's CASCADE will automatically delete related EventDates, EventInterest, and EventSubmission
                event.delete()

                self.stats["deleted_events"] += 1
                self.stats["deleted_event_dates"] += event_dates_count

        except Exception as e:
            logger.error(f"Error deleting event {event.id}: {e}")
            # Close connection on error to ensure clean state
            connection.close()
            raise

    async def validate_events_batch(self, session, events, semaphore):
        """
        Validate a batch of events concurrently with a semaphore to limit concurrency.

        Args:
            session: aiohttp ClientSession
            events: List of Event objects
            semaphore: asyncio.Semaphore to limit concurrent requests
        """

        async def validate_one(event):
            async with semaphore:
                try:
                    return await self.check_event_source(session, event)
                except Exception as e:
                    logger.error(f"Unexpected error processing event {event.id}: {e}")
                    self.stats["errors"] += 1
                    return None, f"Error: {e!s}", event

        results = await asyncio.gather(*[validate_one(event) for event in events])
        return results

    def validate_all_events(self, limit=None, school=None):
        """
        Validate all events in the database using async/concurrent requests.

        Args:
            limit: Maximum number of events to check (for testing)
            school: Filter by school name
        """
        logger.info("=" * 80)
        logger.info("Starting event source validation (CONCURRENT)")
        logger.info(f"Max concurrent requests: {self.max_concurrent}")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info("=" * 80)

        # Query events
        queryset = Events.objects.all().order_by("-id")

        if school:
            queryset = queryset.filter(school=school)
            logger.info(f"Filtering by school: {school}")

        if limit:
            queryset = queryset[:limit]
            logger.info(f"Limiting to {limit} events for testing")

        # Convert to list to avoid database queries in async context
        events = list(queryset)
        total_events = len(events)
        logger.info(f"Total events to check: {total_events}")

        # Run async validation
        asyncio.run(self._async_validate_all(events, total_events))

        # Close stale database connections before deletion
        connection.close()

        # Delete invalid events (must be done in sync context, not inside asyncio.run)
        logger.info(f"\nDeleting {len(self.events_to_delete)} invalid events...")
        for event, reason in self.events_to_delete:
            self.delete_event(event, reason)

        # Print summary
        self.print_summary()

    async def _async_validate_all(self, events, total_events):
        """
        Async method to validate all events concurrently.
        """
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.max_concurrent)

        # Create aiohttp session
        connector = aiohttp.TCPConnector(limit=self.max_concurrent, limit_per_host=5)
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
        ) as session:
            # Process events in batches for better progress tracking
            batch_size = 50
            for i in range(0, len(events), batch_size):
                batch = events[i : i + batch_size]
                logger.info(
                    f"\nProcessing batch {i//batch_size + 1} ({i+1}-{min(i+batch_size, total_events)} of {total_events})"
                )

                results = await self.validate_events_batch(session, batch, semaphore)

                # Process results and mark invalid events for deletion
                for is_valid, reason, event in results:
                    if is_valid is False:
                        logger.info(f"Marking event {event.id} for deletion: {reason}")
                        self.events_to_delete.append((event, reason))

    def print_summary(self):
        """Print validation summary statistics"""
        logger.info("\n" + "=" * 80)
        logger.info("VALIDATION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total events checked:     {self.stats['total_checked']}")
        logger.info(f"Valid URLs:               {self.stats['valid']}")
        logger.info(f"Invalid URLs:             {self.stats['invalid']}")
        logger.info(f"Rate-limited (skipped):   {self.stats['rate_limited']}")
        logger.info(f"Errors/Timeouts:          {self.stats['errors']}")
        logger.info(f"Events deleted:           {self.stats['deleted_events']}")
        logger.info(f"Event dates deleted:      {self.stats['deleted_event_dates']}")
        logger.info("=" * 80)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate event source URLs (with concurrent requests)"
    )
    parser.add_argument(
        "--limit", type=int, help="Limit number of events to check (for testing)"
    )
    parser.add_argument("--school", type=str, help="Filter by school name")
    parser.add_argument(
        "--workers", type=int, default=2, help="Max concurrent requests (default: 2)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Delay between requests in seconds (default: 2.0)",
    )

    args = parser.parse_args()

    validator = EventSourceValidator(
        max_concurrent=args.workers, delay_between_requests=args.delay
    )
    validator.validate_all_events(limit=args.limit, school=args.school)


if __name__ == "__main__":
    main()
