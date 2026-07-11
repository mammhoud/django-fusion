from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_fusion.core.models import BaseModel as DefaultBase
from ceptor_ai.blocks.stream_blocks import BaseStreamBlock
from ceptor_ai.models import ContentBase
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.fields import StreamField
from wagtail.search import index


# -------------------------------------------------------------------
# SCHEDULE MODEL
# -------------------------------------------------------------------
class Schedule(DefaultBase):
    """
    Enhanced Schedule model for class timing with comprehensive validation
    and recurring schedule support.
    """

    class ScheduleType(models.TextChoices):
        ONE_TIME = "one_time", _("One-time Session")
        RECURRING_WEEKLY = "weekly", _("Weekly Recurring")
        RECURRING_BIWEEKLY = "biweekly", _("Bi-weekly Recurring")
        RECURRING_MONTHLY = "monthly", _("Monthly Recurring")
        CUSTOM = "custom", _("Custom Pattern")

    class MeetingPlatform(models.TextChoices):
        ZOOM = "zoom", _("Zoom")
        TEAMS = "teams", _("Microsoft Teams")
        MEET = "meet", _("Google Meet")
        WEBEX = "webex", _("Webex")
        JITSI = "jitsi", _("Jitsi Meet")
        OTHER = "other", _("Other Platform")

    # Basic schedule information
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Schedule Title"),
        help_text=_("Optional descriptive title for this schedule"),
    )

    schedule_type = models.CharField(
        max_length=20,
        choices=ScheduleType.choices,
        default=ScheduleType.ONE_TIME,
        verbose_name=_("Schedule Type"),
        help_text=_("Type of schedule pattern"),
    )

    # Date and time
    start_date = models.DateField(
        verbose_name=_("Start Date"), help_text=_("First occurrence date")
    )

    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("End Date"),
        help_text=_("Optional end date for recurring schedules"),
    )

    start_time = models.TimeField(verbose_name=_("Start Time"), help_text=_("Session start time"))

    end_time = models.TimeField(verbose_name=_("End Time"), help_text=_("Session end time"))

    # Recurrence settings
    recurrence_days = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Recurrence Days"),
        help_text=_("Comma-separated days (0=Sunday, 1=Monday, etc.) for weekly recurrence"),
    )

    recurrence_interval = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Recurrence Interval"),
        help_text=_("Interval for recurrence (e.g., 2 for every 2 weeks)"),
    )

    # Meeting details
    meeting_platform = models.CharField(
        max_length=20,
        choices=MeetingPlatform.choices,
        default=MeetingPlatform.ZOOM,
        verbose_name=_("Meeting Platform"),
    )

    meeting_link = models.URLField(
        blank=True,
        verbose_name=_("Meeting Link"),
        help_text=_("URL for joining the online session"),
    )

    meeting_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Meeting ID"),
        help_text=_("Platform-specific meeting ID"),
    )

    meeting_passcode = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Passcode"),
        help_text=_("Meeting passcode if required"),
    )

    # Status and recording
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Whether this schedule is currently active"),
    )

    is_recorded = models.BooleanField(
        default=False,
        verbose_name=_("Recorded Session"),
        help_text=_("Indicates if sessions are recorded"),
    )

    recording_link = models.URLField(
        blank=True,
        verbose_name=_("Recording Link"),
        help_text=_("Link to session recording"),
    )

    max_participants = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Maximum Participants"),
        help_text=_("Maximum number of participants allowed"),
    )

    # Location (for in-person/hybrid)
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Location"),
        help_text=_("Physical location for in-person sessions"),
    )

    is_online = models.BooleanField(
        default=True,
        verbose_name=_("Online Session"),
        help_text=_("Whether this is an online session"),
    )

    is_hybrid = models.BooleanField(
        default=False,
        verbose_name=_("Hybrid Session"),
        help_text=_("Supports both online and in-person attendance"),
    )

    class Meta:
        verbose_name = _("Schedule")
        verbose_name_plural = _("Schedules")
        ordering = ["start_date", "start_time"]
        indexes = [
            models.Index(fields=["start_date", "start_time"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["schedule_type"]),
            models.Index(fields=["meeting_platform"]),
        ]

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldRowPanel(
                    [
                        FieldPanel("schedule_type"),
                        FieldPanel("is_active"),
                    ]
                ),
            ],
            heading=_("Basic Information"),
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("start_date"),
                        FieldPanel("end_date"),
                    ]
                ),
                FieldRowPanel(
                    [
                        FieldPanel("start_time"),
                        FieldPanel("end_time"),
                    ]
                ),
            ],
            heading=_("Date & Time"),
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("recurrence_days"),
                        FieldPanel("recurrence_interval"),
                    ]
                ),
            ],
            heading=_("Recurrence Settings"),
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("meeting_platform"),
                        FieldPanel("is_online"),
                        FieldPanel("is_hybrid"),
                    ]
                ),
                FieldPanel("meeting_link"),
                FieldRowPanel(
                    [
                        FieldPanel("meeting_id"),
                        FieldPanel("meeting_passcode"),
                    ]
                ),
                FieldPanel("location"),
            ],
            heading=_("Meeting Details"),
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("is_recorded"),
                        FieldPanel("max_participants"),
                    ]
                ),
                FieldPanel("recording_link"),
            ],
            heading=_("Session Settings"),
        ),
    ]

    search_fields = [
        index.SearchField("title"),
        index.SearchField("location"),
        index.SearchField("meeting_id"),
        index.FilterField("start_date"),
        index.FilterField("is_active"),
        index.FilterField("meeting_platform"),
    ]

    # ======================
    # PROPERTIES
    # ======================

    @property
    def duration_minutes(self):
        """Calculate session duration in minutes."""
        if self.start_time and self.end_time:
            start_dt = timezone.datetime.combine(self.start_date, self.start_time)
            end_dt = timezone.datetime.combine(self.start_date, self.end_time)
            duration = end_dt - start_dt
            return int(duration.total_seconds() / 60)
        return 0

    @property
    def duration_display(self):
        """Get human-readable duration."""
        minutes = self.duration_minutes
        if minutes >= 60:
            hours = minutes // 60
            mins = minutes % 60
            if mins > 0:
                return f"{hours}h {mins}m"
            return f"{hours}h"
        return f"{minutes}m"

    @property
    def is_recurring(self):
        """Check if this is a recurring schedule."""
        return self.schedule_type != self.ScheduleType.ONE_TIME

    @property
    def is_current(self):
        """Check if schedule is currently relevant."""
        today = timezone.now().date()
        if self.end_date and today > self.end_date:
            return False
        return self.is_active and today >= self.start_date

    @property
    def is_ongoing(self):
        """Check if there's a session happening right now."""
        now = timezone.now()
        today = now.date()
        current_time = now.time()

        if self.start_date <= today <= (self.end_date or today):
            if self.start_time <= current_time <= self.end_time:
                return True
        return False

    @property
    def next_occurrence(self):
        """Get the next scheduled occurrence."""
        if not self.is_current:
            return None

        today = timezone.now().date()
        current_time = timezone.now().time()

        # For one-time schedules
        if self.schedule_type == self.ScheduleType.ONE_TIME:
            if self.start_date > today or (
                self.start_date == today and self.start_time > current_time
            ):
                return timezone.datetime.combine(self.start_date, self.start_time)
            return None

        # For recurring schedules - simplified calculation
        # In a real implementation, you'd want more sophisticated recurrence calculation
        return timezone.datetime.combine(self.start_date, self.start_time)

    @property
    def platform_icon(self):
        """Get platform icon class."""
        icons = {
            self.MeetingPlatform.ZOOM: "fa-video",
            self.MeetingPlatform.TEAMS: "fa-microsoft",
            self.MeetingPlatform.MEET: "fa-video",
            self.MeetingPlatform.WEBEX: "fa-video",
            self.MeetingPlatform.JITSI: "fa-video",
            self.MeetingPlatform.OTHER: "fa-video",
        }
        return icons.get(self.meeting_platform, "fa-video")

    # ======================
    # METHODS
    # ======================

    def clean(self):
        """Validate schedule data."""
        super().clean()

        # Date validation
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": _("End date cannot be before start date.")})

        # Time validation
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError({"end_time": _("End time must be after start time.")})

        # Recurrence validation
        if self.is_recurring and not self.end_date:
            raise ValidationError({"end_date": _("Recurring schedules must have an end date.")})

        # Hybrid session validation
        if self.is_hybrid and not self.location:
            raise ValidationError({"location": _("Hybrid sessions must have a physical location.")})

    def generate_occurrences(self, from_date=None, to_date=None):
        """Generate all schedule occurrences between dates."""
        # This is a simplified implementation
        # In production, you'd want a more robust recurrence calculation
        occurrences = []

        if self.schedule_type == self.ScheduleType.ONE_TIME:
            occurrences.append(
                {
                    "date": self.start_date,
                    "start_time": self.start_time,
                    "end_time": self.end_time,
                }
            )

        return occurrences

    def get_upcoming_occurrences(self, limit=10):
        """Get upcoming occurrences for this schedule."""
        today = timezone.now().date()
        occurrences = self.generate_occurrences(from_date=today)
        return occurrences[:limit]

    def __str__(self):
        if self.title:
            return f"{self.title} - {self.start_date} {self.start_time}"
        return f"Schedule {self.code} - {self.start_date} {self.start_time}"

    # ======================
    # CLASS METHODS
    # ======================

    @classmethod
    def get_todays_sessions(cls):
        """Return today's scheduled sessions."""
        today = timezone.now().date()
        return cls.objects.filter(start_date__lte=today, end_date__gte=today, is_active=True)

    @classmethod
    def get_ongoing_sessions(cls):
        """Return currently ongoing sessions."""
        now = timezone.now()
        today = now.date()
        current_time = now.time()

        return cls.objects.filter(
            start_date__lte=today,
            end_date__gte=today,
            start_time__lte=current_time,
            end_time__gte=current_time,
            is_active=True,
        )

    @classmethod
    def get_upcoming_sessions(cls, hours_ahead=24):
        """Return sessions starting in the next specified hours."""
        now = timezone.now()
        end_time = now + timezone.timedelta(hours=hours_ahead)

        return cls.objects.filter(
            start_date=now.date(),
            start_time__gte=now.time(),
            start_time__lte=end_time.time(),
            is_active=True,
        ).order_by("start_time")


# -------------------------------------------------------------------
# CLASS MODEL
# -------------------------------------------------------------------
class Classes(ContentBase):
    """
    Enhanced Class model representing a specific class instance for a course module.
    Supports multiple instructors, rich content, and comprehensive management.
    """

    class ClassStatus(models.TextChoices):
        DRAFT = "draft", _("Draft")
        SCHEDULED = "scheduled", _("Scheduled")
        LIVE = "live", _("Live")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")
        ARCHIVED = "archived", _("Archived")

    class ClassType(models.TextChoices):
        LECTURE = "lecture", _("Lecture")
        WORKSHOP = "workshop", _("Workshop")
        LAB = "lab", _("Lab Session")
        SEMINAR = "seminar", _("Seminar")
        TUTORIAL = "tutorial", _("Tutorial")
        DISCUSSION = "discussion", _("Discussion")
        OTHER = "other", _("Other")

    # Core relationships
    course = models.ForeignKey(
        "lms.Course",
        on_delete=models.CASCADE,
        related_name="classes",
        verbose_name=_("Course"),
        help_text=_("Parent course for this class"),
    )

    module = models.ForeignKey(
        "lms.Module",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classes",
        verbose_name=_("Module"),
        help_text=_("Optional parent module"),
    )

    # Class metadata
    class_type = models.CharField(
        max_length=20,
        choices=ClassType.choices,
        default=ClassType.LECTURE,
        verbose_name=_("Class Type"),
    )

    status = models.CharField(
        max_length=20,
        choices=ClassStatus.choices,
        default=ClassStatus.DRAFT,
        verbose_name=_("Status"),
    )

    sequence = models.PositiveIntegerField(
        default=0, verbose_name=_("Sequence"), help_text=_("Order within course/module")
    )

    # Instructors and management
    primary_instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="primary_classes",
        verbose_name=_("Primary Instructor"),
        help_text=_("Main instructor responsible for this class"),
    )

    co_instructors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="co_taught_classes",
        verbose_name=_("Co-instructors"),
        help_text=_("Additional instructors assisting with this class"),
    )

    # Schedule
    schedule = models.OneToOneField(
        "Schedule",
        on_delete=models.CASCADE,
        related_name="class_instance",
        verbose_name=_("Schedule"),
        help_text=_("Schedule for this class instance"),
    )

    # Content and materials
    objectives = models.TextField(
        blank=True,
        verbose_name=_("Learning Objectives"),
        help_text=_("What students will learn in this class"),
    )

    materials = StreamField(
        BaseStreamBlock(),
        blank=True,
        use_json_field=True,
        verbose_name=_("Class Materials"),
        help_text=_("Additional materials and resources for this class"),
    )

    prerequisites = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        verbose_name=_("Prerequisites"),
        help_text=_("Classes that should be completed before this one"),
    )

    # Settings
    max_students = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Maximum Students"),
        help_text=_("Maximum number of students allowed"),
    )

    is_mandatory = models.BooleanField(
        default=True,
        verbose_name=_("Mandatory"),
        help_text=_("Whether attendance is mandatory"),
    )

    requires_registration = models.BooleanField(
        default=True,
        verbose_name=_("Requires Registration"),
        help_text=_("Whether students need to register for this class"),
    )

    class Meta:
        verbose_name = _("Class")
        verbose_name_plural = _("Classes")
        ordering = ["course", "sequence", "created_at"]
        unique_together = ["course", "sequence"]
        indexes = [
            models.Index(fields=["course", "sequence"]),
            models.Index(fields=["status"]),
            models.Index(fields=["class_type"]),
            models.Index(fields=["primary_instructor"]),
        ]

    panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("course"),
                        FieldPanel("module"),
                    ]
                ),
                FieldRowPanel(
                    [
                        FieldPanel("class_type"),
                        FieldPanel("status"),
                        FieldPanel("sequence"),
                    ]
                ),
            ],
            heading=_("Basic Information"),
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("primary_instructor"),
                        FieldPanel("co_instructors"),
                    ]
                ),
            ],
            heading=_("Instructors"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("schedule"),
            ],
            heading=_("Schedule"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("description"),
                FieldPanel("objectives"),
            ],
            heading=_("Content"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("materials"),
            ],
            heading=_("Materials & Resources"),
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("max_students"),
                        FieldPanel("is_mandatory"),
                        FieldPanel("requires_registration"),
                    ]
                ),
                FieldPanel("prerequisites"),
            ],
            heading=_("Settings"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("is_published"),
                FieldPanel("order"),
            ],
            heading=_("Publication"),
        ),
    ]

    # Override edit_handler to avoid inheriting content_panels/promote_panels/settings_panels
    # from ContentBase (which are only valid on Page subclasses, not snippets).
    edit_handler = TabbedInterface([
        ObjectList([
            MultiFieldPanel([
                FieldRowPanel([FieldPanel("course"), FieldPanel("module")]),
                FieldRowPanel([FieldPanel("class_type"), FieldPanel("status"), FieldPanel("sequence")]),
            ], heading=_("Basic Information")),
            MultiFieldPanel([
                FieldRowPanel([FieldPanel("primary_instructor"), FieldPanel("co_instructors")]),
            ], heading=_("Instructors")),
            MultiFieldPanel([FieldPanel("schedule")], heading=_("Schedule")),
            MultiFieldPanel([
                FieldPanel("title"), FieldPanel("description"), FieldPanel("objectives"),
            ], heading=_("Content")),
            MultiFieldPanel([FieldPanel("materials")], heading=_("Materials & Resources")),
        ], heading=_("Class")),
        ObjectList([
            MultiFieldPanel([
                FieldRowPanel([FieldPanel("max_students"), FieldPanel("is_mandatory"), FieldPanel("requires_registration")]),
                FieldPanel("prerequisites"),
            ], heading=_("Settings")),
            MultiFieldPanel([FieldPanel("is_published"), FieldPanel("order")], heading=_("Publication")),
        ], heading=_("Settings")),
    ])

    search_fields = [
        index.SearchField("title"),
        index.SearchField("description"),
        index.SearchField("objectives"),
        index.FilterField("status"),
        index.FilterField("class_type"),
        index.RelatedFields(
            "course",
            [
                index.SearchField("title"),
            ],
        ),
        index.RelatedFields(
            "primary_instructor",
            [
                index.SearchField("first_name"),
                index.SearchField("last_name"),
            ],
        ),
    ]

    # ======================
    # PROPERTIES
    # ======================

    @property
    def all_instructors(self):
        """Get all instructors (primary + co-instructors)."""
        instructors = []
        if self.primary_instructor:
            instructors.append(self.primary_instructor)
        instructors.extend(list(self.co_instructors.all()))
        return instructors

    @property
    def instructor_names(self):
        """Get formatted instructor names."""
        names = [str(instructor) for instructor in self.all_instructors]
        return ", ".join(names) if names else _("No instructors assigned")

    @property
    def is_upcoming(self):
        """Check if class is upcoming."""
        return self.status == self.ClassStatus.SCHEDULED

    @property
    def is_live(self):
        """Check if class is currently live."""
        return self.status == self.ClassStatus.LIVE

    @property
    def is_completed(self):
        """Check if class is completed."""
        return self.status == self.ClassStatus.COMPLETED

    @property
    def student_count(self):
        """Get current student count (to be implemented with registration system)."""
        return 0  # Placeholder

    @property
    def available_spots(self):
        """Calculate available spots."""
        if self.max_students:
            return max(0, self.max_students - self.student_count)
        return None

    @property
    def is_full(self):
        """Check if class is full."""
        if self.max_students:
            return self.student_count >= self.max_students
        return False

    # ======================
    # METHODS
    # ======================

    def clean(self):
        """Validate class data."""
        super().clean()

        # Ensure module belongs to course
        if self.module and self.module.course != self.course:
            raise ValidationError({"module": _("Selected module must belong to the same course.")})

        # Validate sequence uniqueness
        if self.sequence and self.course:
            existing = Classes.objects.filter(course=self.course, sequence=self.sequence).exclude(
                pk=self.pk
            )

            if existing.exists():
                raise ValidationError(
                    {"sequence": _("A class with this sequence already exists in the course.")}
                )

    def save(self, *args, **kwargs):
        """Auto-generate code prefix and handle status updates."""
        self.code_prefix = "CLS"

        # Auto-update status based on schedule
        if self.schedule:
            if self.schedule.is_ongoing and self.status != self.ClassStatus.LIVE:
                self.status = self.ClassStatus.LIVE
            elif (
                self.schedule.start_date < timezone.now().date()
                and self.status == self.ClassStatus.SCHEDULED
            ):
                self.status = self.ClassStatus.COMPLETED

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Get URL for class detail page."""
        from django.urls import reverse

        return reverse("class-detail", kwargs={"pk": self.pk})

    def can_register(self):
        """Check if registration is possible."""
        return (
            self.requires_registration
            and self.status == self.ClassStatus.SCHEDULED
            and not self.is_full
            and self.is_published
        )

    def __str__(self):
        return f"{self.course.title} - {self.title} ({self.get_class_type_display()})"


# # -------------------------------------------------------------------
# # CLASS ATTENDANCE MODEL (Optional through model)
# # -------------------------------------------------------------------
# class ClassAttendance(DefaultBase):
#     """
#     Track student attendance for classes.
#     """

#     class_instance = models.ForeignKey(
#         Classes, on_delete=models.CASCADE, related_name="attendances"
#     )

#     student = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="class_attendances",
#     )

#     attended = models.BooleanField(default=False)
#     joined_at = models.DateTimeField(null=True, blank=True)
#     left_at = models.DateTimeField(null=True, blank=True)
#     notes = models.TextField(blank=True)

#     class Meta:
#         verbose_name = _("Class Attendance")
#         verbose_name_plural = _("Class Attendances")
#         unique_together = ["class_instance", "student"]

#     def __str__(self):
#         status = "Attended" if self.attended else "Absent"
#         return f"{self.student} - {self.class_instance} ({status})"
