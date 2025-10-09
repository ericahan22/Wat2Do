import os
from datetime import date, datetime, timedelta

import django
import requests
from django.conf import settings

# Setup Django if not already configured
if not settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")
    django.setup()

from example.models import Events


class EmailService:
    def __init__(self):
        self.api_key = os.getenv("RESEND_API_KEY")
        self.from_email = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")
        self.base_url = "https://api.resend.com/emails"

    def _get_events_added_today(self):
        """Fetch events that were added to the database today"""
        today = date.today()

        # Get events added today, ordered by date and start time
        events = (
            Events.objects.filter(added_at__date=today)
            .select_related()
            .order_by("date", "start_time")
        )

        events_data = []
        for event in events:
            # Format the event data for email template
            event_date = event.date.strftime("%B %d, %Y")

            # Format time range
            start_time = event.start_time.strftime("%I:%M %p").lstrip("0")
            if event.end_time:
                end_time = event.end_time.strftime("%I:%M %p").lstrip("0")
                time_range = f"{start_time} - {end_time}"
            else:
                time_range = f"Starting at {start_time}"

            # Get club name from club_handle or use club_type as fallback
            club_name = event.club_handle or event.club_type or "Unknown Club"

            events_data.append(
                {
                    "name": event.name,
                    "date": event_date,
                    "time": time_range,
                    "location": event.location,
                    "description": event.description or "No description available.",
                    "club": club_name,
                    "image_url": event.image_url,
                }
            )

        return events_data

    def get_mock_events(self):
        """Generate mock event data for the newsletter (DEPRECATED - use get_events_added_today instead)"""
        today = datetime.now()
        return [
            {
                "name": "Tech Talks: AI & Machine Learning",
                "date": (today + timedelta(days=2)).strftime("%B %d, %Y"),
                "time": "6:00 PM - 8:00 PM",
                "location": "DC 1302",
                "description": "Join us for an exciting discussion on the latest trends in AI and ML.",
                "club": "UW Tech Club",
            },
            {
                "name": "Free Pizza Social",
                "date": (today + timedelta(days=3)).strftime("%B %d, %Y"),
                "time": "5:00 PM - 7:00 PM",
                "location": "SLC Great Hall",
                "description": "Come grab some free pizza and meet fellow students!",
                "club": "WUSA",
            },
            {
                "name": "Career Fair 2025",
                "date": (today + timedelta(days=5)).strftime("%B %d, %Y"),
                "time": "10:00 AM - 4:00 PM",
                "location": "PAC",
                "description": "Meet top employers and explore career opportunities.",
                "club": "Co-op Office",
            },
            {
                "name": "Hackathon Kickoff",
                "date": (today + timedelta(days=7)).strftime("%B %d, %Y"),
                "time": "9:00 AM - 9:00 PM",
                "location": "E7 Building",
                "description": "24-hour hackathon with amazing prizes and workshops!",
                "club": "Hack the North",
            },
        ]

    def generate_email_html(self, events, unsubscribe_token):
        """Generate HTML email from events data"""
        events_html = ""
        for event in events:
            # Add event image if available
            image_html = ""
            if event.get('image_url'):
                image_html = f"""
                    <img
                      src="{event['image_url']}"
                      alt="{event['name']}"
                      style="width:100%;max-width:100%;height:200px;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block"
                    />
                    """

            events_html += f"""
            <table
              align="center"
              width="100%"
              border="0"
              cellpadding="0"
              cellspacing="0"
              role="presentation"
              style="background:#f8f9fa;border-radius:8px;padding:20px;margin-bottom:20px">
              <tbody>
                <tr>
                  <td>
                    {image_html}
                    <h3
                      style="margin:0 0 8px;font-weight:bold;font-size:18px;line-height:24px;color:#0c0d0e">
                      {event['name']}
                    </h3>
                    <p
                      style="font-size:14px;line-height:20px;color:#6a737c;margin:4px 0">
                      <strong>📅 {event['date']}</strong> at {event['time']}
                    </p>
                    <p
                      style="font-size:14px;line-height:20px;color:#6a737c;margin:4px 0">
                      <strong>📍 {event['location']}</strong>
                    </p>
                    <p
                      style="font-size:14px;line-height:20px;color:#3c3f44;margin:8px 0 4px 0">
                      {event['description']}
                    </p>
                    <p
                      style="font-size:13px;line-height:18px;color:#9199a1;margin:4px 0 0 0">
                      Hosted by {event['club']}
                    </p>
                  </td>
                </tr>
              </tbody>
            </table>
            """

        return f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html dir="ltr" lang="en">
  <head>
    <meta content="text/html; charset=UTF-8" http-equiv="Content-Type" />
    <meta name="x-apple-disable-message-reformatting" />
  </head>
  <body style="background-color:#f3f3f5">
    <table
      border="0"
      width="100%"
      cellpadding="0"
      cellspacing="0"
      role="presentation"
      align="center">
      <tbody>
        <tr>
          <td
            style="background-color:#f3f3f5;font-family:HelveticaNeue,Helvetica,Arial,sans-serif">
            <div
              style="display:none;overflow:hidden;line-height:1px;opacity:0;max-height:0;max-width:0"
              data-skip-in-text="true">
              Your daily UWaterloo events digest
            </div>
            <table
              align="center"
              width="100%"
              border="0"
              cellpadding="0"
              cellspacing="0"
              role="presentation"
              style="max-width:100%;width:680px;margin:0 auto;background-color:#ffffff">
              <tbody>
                <tr style="width:100%">
                  <td>
                    <table
                      align="center"
                      width="100%"
                      border="0"
                      cellpadding="0"
                      cellspacing="0"
                      role="presentation"
                      style="display:flex;background:#f3f3f5;padding:20px 30px">
                      <tbody>
                        <tr>
                          <td>
                            <h1 style="font-size:28px;font-weight:bold;color:#0c0d0e;margin:0">
                              Wat2Do 🎉
                            </h1>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <table
                      align="center"
                      width="100%"
                      border="0"
                      cellpadding="0"
                      cellspacing="0"
                      role="presentation"
                      style="border-radius:5px 5px 0 0;display:flex;flex-direciont:column;background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                      <tbody>
                        <tr>
                          <td>
                            <table
                              align="center"
                              width="100%"
                              border="0"
                              cellpadding="0"
                              cellspacing="0"
                              role="presentation">
                              <tbody style="width:100%">
                                <tr style="width:100%">
                                  <td
                                    data-id="__react-email-column"
                                    style="padding:40px 30px">
                                    <h1
                                      style="color:#fff;font-size:32px;font-weight:bold;line-height:38px;margin:0 0 12px 0">
                                      Welcome to Wat2Do! 🎓
                                    </h1>
                                    <p
                                      style="font-size:18px;line-height:26px;color:#fff;margin:0">
                                      Your daily digest of upcoming events at UWaterloo
                                    </p>
                                  </td>
                                </tr>
                              </tbody>
                            </table>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <table
                      align="center"
                      width="100%"
                      border="0"
                      cellpadding="0"
                      cellspacing="0"
                      role="presentation"
                      style="padding:30px 30px 40px 30px">
                      <tbody>
                        <tr>
                          <td>
                            <h2
                              style="margin:0 0 20px;font-weight:bold;font-size:24px;line-height:28px;color:#0c0d0e">
                              📅 Today's New Events
                            </h2>
                            <p
                              style="font-size:15px;line-height:22px;color:#3c3f44;margin:0 0 24px 0">
                              Here are some exciting events that were just added to our platform. Don't miss out!
                            </p>
                            
                            {events_html}
                            
                            <hr
                              style="width:100%;border:none;border-top:1px solid #eaeaea;margin:30px 0" />
                            
                            <table
                              align="center"
                              width="100%"
                              border="0"
                              cellpadding="0"
                              cellspacing="0"
                              role="presentation"
                              style="margin-top:24px;display:block">
                              <tbody>
                                <tr>
                                  <td style="text-align:center">
                                    <a
                                      href="https://wat2do.ca"
                                      style="color:#fff;text-decoration-line:none;background-color:#667eea;border:1px solid #5568d3;font-size:16px;line-height:16px;padding:14px 24px;border-radius:6px;display:inline-block;font-weight:600"
                                      target="_blank"
                                      >View All Events on Wat2Do</a
                                    >
                                  </td>
                                </tr>
                              </tbody>
                            </table>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </td>
                </tr>
              </tbody>
            </table>
            <table
              align="center"
              width="100%"
              border="0"
              cellpadding="0"
              cellspacing="0"
              role="presentation"
              style="width:680px;max-width:100%;margin:32px auto 0 auto;padding:0 30px">
              <tbody>
                <tr>
                  <td>
                    <p
                      style="font-size:12px;line-height:18px;color:#9199a1;margin:0;margin-bottom:16px">
                      You're receiving this email because you subscribed to Wat2Do newsletter for UWaterloo events.
                    </p>
                    <a
                      href="https://wat2do.ca"
                      style="color:#9199a1;text-decoration-line:none;display:inline-block;text-decoration:underline;font-size:12px;margin-right:16px"
                      target="_blank"
                      >Visit Wat2Do</a
                    ><a
                      href="https://wat2do.ca/unsubscribe/{unsubscribe_token}"
                      style="color:#9199a1;text-decoration-line:none;display:inline-block;text-decoration:underline;font-size:12px;margin-right:16px"
                      target="_blank"
                      >Unsubscribe</a
                    >
                    <hr
                      style="width:100%;border:none;border-top:1px solid #eaeaea;margin:24px 0;border-color:#d6d8db" />
                    <p
                      style="font-size:12px;line-height:18px;margin:4px 0;color:#9199a1">
                      <strong>Wat2Do</strong> - Your guide to UWaterloo events
                    </p>
                    <p
                      style="font-size:11px;line-height:14px;border-radius:3px;border:1px solid #d6d9dc;padding:8px 10px;font-family:Consolas,monospace;color:#667eea;max-width:min-content;margin:16px 0 32px 0">
                      Made with 💜 for UWaterloo
                    </p>
                  </td>
                </tr>
              </tbody>
            </table>
          </td>
        </tr>
      </tbody>
    </table>
  </body>
</html>"""

    def generate_newsletter_html(self, events, unsubscribe_token):
        """Generate HTML email for daily newsletter (different from welcome email)"""
        events_html = ""
        for event in events:
            # Add event image if available
            image_html = ""
            if event.get('image_url'):
                image_html = f"""
                    <img
                      src="{event['image_url']}"
                      alt="{event['name']}"
                      style="width:100%;max-width:100%;height:200px;object-fit:cover;border-radius:8px;margin-bottom:16px;display:block"
                    />
                    """

            events_html += f"""
            <table
              align="center"
              width="100%"
              border="0"
              cellpadding="0"
              cellspacing="0"
              role="presentation"
              style="background:#f8f9fa;border-radius:8px;padding:20px;margin-bottom:20px">
              <tbody>
                <tr>
                  <td>
                    {image_html}
                    <h3
                      style="margin:0 0 8px;font-weight:bold;font-size:18px;line-height:24px;color:#0c0d0e">
                      {event['name']}
                    </h3>
                    <p
                      style="font-size:14px;line-height:20px;color:#6a737c;margin:4px 0">
                      <strong>📅 {event['date']}</strong> at {event['time']}
                    </p>
                    <p
                      style="font-size:14px;line-height:20px;color:#6a737c;margin:4px 0">
                      <strong>📍 {event['location']}</strong>
                    </p>
                    <p
                      style="font-size:14px;line-height:20px;color:#3c3f44;margin:8px 0 4px 0">
                      {event['description']}
                    </p>
                    <p
                      style="font-size:13px;line-height:18px;color:#9199a1;margin:4px 0 0 0">
                      Hosted by {event['club']}
                    </p>
                  </td>
                </tr>
              </tbody>
            </table>
            """

        return f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html dir="ltr" lang="en">
  <head>
    <meta content="text/html; charset=UTF-8" http-equiv="Content-Type" />
    <meta name="x-apple-disable-message-reformatting" />
  </head>
  <body style="background-color:#f3f3f5">
    <table
      border="0"
      width="100%"
      cellpadding="0"
      cellspacing="0"
      role="presentation"
      align="center">
      <tbody>
        <tr>
          <td
            style="background-color:#f3f3f5;font-family:HelveticaNeue,Helvetica,Arial,sans-serif">
            <div
              style="display:none;overflow:hidden;line-height:1px;opacity:0;max-height:0;max-width:0"
              data-skip-in-text="true">
              Your daily UWaterloo events digest
            </div>
            <table
              align="center"
              width="100%"
              border="0"
              cellpadding="0"
              cellspacing="0"
              role="presentation"
              style="max-width:100%;width:680px;margin:0 auto;background-color:#ffffff">
              <tbody>
                <tr style="width:100%">
                  <td>
                    <table
                      align="center"
                      width="100%"
                      border="0"
                      cellpadding="0"
                      cellspacing="0"
                      role="presentation"
                      style="display:flex;background:#f3f3f5;padding:20px 30px">
                      <tbody>
                        <tr>
                          <td>
                            <h1 style="font-size:28px;font-weight:bold;color:#0c0d0e;margin:0">
                              Wat2Do 🎉
                            </h1>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <table
                      align="center"
                      width="100%"
                      border="0"
                      cellpadding="0"
                      cellspacing="0"
                      role="presentation"
                      style="border-radius:5px 5px 0 0;display:flex;flex-direciont:column;background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                      <tbody>
                        <tr>
                          <td>
                            <table
                              align="center"
                              width="100%"
                              border="0"
                              cellpadding="0"
                              cellspacing="0"
                              role="presentation">
                              <tbody style="width:100%">
                                <tr style="width:100%">
                                  <td
                                    data-id="__react-email-column"
                                    style="padding:40px 30px">
                                    <h1
                                      style="color:#fff;font-size:32px;font-weight:bold;line-height:38px;margin:0 0 12px 0">
                                      Today's New Events 🎓
                                    </h1>
                                    <p
                                      style="font-size:18px;line-height:26px;color:#fff;margin:0">
                                      Your daily digest of upcoming events at UWaterloo
                                    </p>
                                  </td>
                                </tr>
                              </tbody>
                            </table>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <table
                      align="center"
                      width="100%"
                      border="0"
                      cellpadding="0"
                      cellspacing="0"
                      role="presentation"
                      style="padding:30px 30px 40px 30px">
                      <tbody>
                        <tr>
                          <td>
                            <h2
                              style="margin:0 0 20px;font-weight:bold;font-size:24px;line-height:28px;color:#0c0d0e">
                              📅 Today's New Events
                            </h2>
                            <p
                              style="font-size:15px;line-height:22px;color:#3c3f44;margin:0 0 24px 0">
                              Here are some exciting events that were just added to our platform. Don't miss out!
                            </p>
                            
                            {events_html}
                            
                            <hr
                              style="width:100%;border:none;border-top:1px solid #eaeaea;margin:30px 0" />
                            
                            <table
                              align="center"
                              width="100%"
                              border="0"
                              cellpadding="0"
                              cellspacing="0"
                              role="presentation"
                              style="margin-top:24px;display:block">
                              <tbody>
                                <tr>
                                  <td style="text-align:center">
                                    <a
                                      href="https://wat2do.ca"
                                      style="color:#fff;text-decoration-line:none;background-color:#667eea;border:1px solid #5568d3;font-size:16px;line-height:16px;padding:14px 24px;border-radius:6px;display:inline-block;font-weight:600"
                                      target="_blank"
                                      >View All Events on Wat2Do</a
                                    >
                                  </td>
                                </tr>
                              </tbody>
                            </table>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </td>
                </tr>
              </tbody>
            </table>
            <table
              align="center"
              width="100%"
              border="0"
              cellpadding="0"
              cellspacing="0"
              role="presentation"
              style="width:680px;max-width:100%;margin:32px auto 0 auto;padding:0 30px">
              <tbody>
                <tr>
                  <td>
                    <p
                      style="font-size:12px;line-height:18px;color:#9199a1;margin:0;margin-bottom:16px">
                      You're receiving this email because you subscribed to Wat2Do newsletter for UWaterloo events.
                    </p>
                    <a
                      href="https://wat2do.ca"
                      style="color:#9199a1;text-decoration-line:none;display:inline-block;text-decoration:underline;font-size:12px;margin-right:16px"
                      target="_blank"
                      >Visit Wat2Do</a
                    ><a
                      href="https://wat2do.ca/unsubscribe/{unsubscribe_token}"
                      style="color:#9199a1;text-decoration-line:none;display:inline-block;text-decoration:underline;font-size:12px;margin-right:16px"
                      target="_blank"
                      >Unsubscribe</a
                    >
                    <hr
                      style="width:100%;border:none;border-top:1px solid #eaeaea;margin:24px 0;border-color:#d6d8db" />
                    <p
                      style="font-size:12px;line-height:18px;margin:4px 0;color:#9199a1">
                      <strong>Wat2Do</strong> - Your guide to UWaterloo events
                    </p>
                    <p
                      style="font-size:11px;line-height:14px;border-radius:3px;border:1px solid #d6d9dc;padding:8px 10px;font-family:Consolas,monospace;color:#667eea;max-width:min-content;margin:16px 0 32px 0">
                      Made with 💜 for UWaterloo
                    </p>
                  </td>
                </tr>
              </tbody>
            </table>
          </td>
        </tr>
      </tbody>
    </table>
  </body>
</html>"""

    def send_welcome_email(self, to_email, unsubscribe_token):
        """Send welcome email with events added today to new subscriber"""
        if not self.api_key:
            print("Warning: RESEND_API_KEY not set. Email not sent.")
            return False

        events = self._get_events_added_today()
        html_content = self.generate_email_html(events, unsubscribe_token)

        payload = {
            "from": f"Welcome to Wat2Do <{self.from_email}>",
            "to": [to_email],
            "subject": "Welcome to Wat2Do! 🎉 Your Daily UWaterloo Events",
            "html": html_content,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error sending email: {e}")
            return False

    def send_newsletter_email(self, to_email, unsubscribe_token):
        """Send newsletter email with events added today to subscriber"""
        if not self.api_key:
            print("Warning: RESEND_API_KEY not set. Email not sent.")
            return False

        events = self._get_events_added_today()
        html_content = self.generate_newsletter_html(events, unsubscribe_token)

        payload = {
            "from": f"Today's Events at Wat2Do <{self.from_email}>",
            "to": [to_email],
            "subject": "Today's New Events at UWaterloo 🎓",
            "html": html_content,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error sending email: {e}")
            return False


# Singleton instance
email_service = EmailService()
