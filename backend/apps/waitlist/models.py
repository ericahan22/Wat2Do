from django.db import models


# School configuration with slug, display name, and valid email domains
SCHOOL_CONFIG = {
    "utsg": {
        "name": "University of Toronto St. George",
        "domains": ["utoronto.ca", "mail.utoronto.ca"],
    },
    "york-university": {
        "name": "York University",
        "domains": ["yorku.ca"],
    },
    "mit": {
        "name": "Massachusetts Institute of Technology",
        "domains": ["mit.edu"],
    },
    "harvard": {
        "name": "Harvard University",
        "domains": ["harvard.edu"],
    },
    "stanford": {
        "name": "Stanford University",
        "domains": ["stanford.edu"],
    },
}


class WaitlistEntry(models.Model):
    email = models.EmailField(help_text="University email address")
    school_slug = models.CharField(
        max_length=100,
        help_text="URL-friendly school identifier (e.g., 'university-of-waterloo')",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "waitlist_entries"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["email", "school_slug"],
                name="unique_email_per_school",
            )
        ]
        indexes = [
            models.Index(fields=["school_slug"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"WaitlistEntry({self.get_email_display()}, {self.school_slug})"

    @property
    def school_name(self):
        """Get the display name for this school"""
        config = SCHOOL_CONFIG.get(self.school_slug)
        return config["name"] if config else self.school_slug

    def get_email_display(self):
        """Return a masked version of the email for display purposes"""
        if self.email:
            local, domain = self.email.split("@", 1)
            masked_local = (
                local[:2] + "*" * (len(local) - 2) if len(local) > 2 else local
            )
            return f"{masked_local}@{domain}"
        return "***@***"

    @classmethod
    def is_valid_school(cls, school_slug):
        """Check if a school slug is valid"""
        return school_slug in SCHOOL_CONFIG

    @classmethod
    def get_valid_domains(cls, school_slug):
        """Get valid email domains for a school"""
        config = SCHOOL_CONFIG.get(school_slug)
        return config["domains"] if config else []

    @classmethod
    def validate_email_for_school(cls, email, school_slug):
        """
        Validate that an email belongs to the specified school.
        Returns (is_valid, error_message)
        """
        if not cls.is_valid_school(school_slug):
            return False, "Invalid school"

        email = email.lower().strip()
        if "@" not in email:
            return False, "Invalid email format"

        domain = email.split("@")[1]
        valid_domains = cls.get_valid_domains(school_slug)

        if domain not in valid_domains:
            school_name = SCHOOL_CONFIG[school_slug]["name"]
            expected = ", ".join(valid_domains)
            return False, f"Please use your {school_name} email ({expected})"

        return True, None

    @classmethod
    def create_entry(cls, email, school_slug):
        """Create a new waitlist entry after validation"""
        return cls.objects.create(
            email=email.lower().strip(),
            school_slug=school_slug,
        )
