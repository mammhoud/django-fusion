# Project-specific imports removed
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.search import index

from crafts_ai.http.handlers.models.manage_company import Department
from crafts_ai.content.models.default import DefaultBase


# -------------------------------------------------------------------
# TEAM MEMBERSHIP MODEL
# -------------------------------------------------------------------
class TeamMembership(DefaultBase):
    """
    Enhanced Team membership through model with roles, permissions, and membership details.
    """

    class MemberRole(models.TextChoices):
        MEMBER = "member", _("Team Member")
        LEADER = "leader", _("Team Leader")
        DEPUTY_LEADER = "deputy_leader", _("Deputy Leader")
        MENTOR = "mentor", _("Mentor")
        CONTRIBUTOR = "contributor", _("Contributor")
        ADVISOR = "advisor", _("Advisor")
        GUEST = "guest", _("Guest Member")

    class MembershipStatus(models.TextChoices):
        ACTIVE = "active", _("Active")
        PENDING = "pending", _("Pending Approval")
        INACTIVE = "inactive", _("Inactive")
        ON_LEAVE = "on_leave", _("On Leave")
        ALUMNI = "alumni", _("Alumni")

    person = models.ForeignKey(
        getattr(settings, 'PROFILE_MODEL', 'auth.User'),
        on_delete=models.CASCADE,
        limit_choices_to={"type": "EMP", "is_active": True},
        related_name="team_memberships",
        verbose_name=_("Team Member"),
    )

    team = ParentalKey(
        "Team", on_delete=models.CASCADE, related_name="memberships", verbose_name=_("Team")
    )

    role = models.CharField(
        max_length=20,
        choices=MemberRole.choices,
        default=MemberRole.MEMBER,
        verbose_name=_("Team Role"),
        help_text=_("Primary role within the team"),
    )

    status = models.CharField(
        max_length=20,
        choices=MembershipStatus.choices,
        default=MembershipStatus.ACTIVE,
        verbose_name=_("Membership Status"),
        help_text=_("Current status of team membership"),
    )

    date_joined = models.DateField(
        default=timezone.now,
        verbose_name=_("Join Date"),
        help_text=_("Date when member joined the team"),
    )

    date_left = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Leave Date"),
        help_text=_("Date when member left the team (if applicable)"),
    )

    is_primary_team = models.BooleanField(
        default=False,
        verbose_name=_("Primary Team"),
        help_text=_("This is the member's primary team assignment"),
    )

    allocation_percentage = models.PositiveIntegerField(
        default=100,
        verbose_name=_("Time Allocation %"),
        help_text=_("Percentage of time allocated to this team (0-100)"),
    )

    responsibilities = models.TextField(
        blank=True,
        verbose_name=_("Key Responsibilities"),
        help_text=_("Primary responsibilities within the team"),
    )

    skills = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Team-specific Skills"),
        help_text=_("Skills specifically relevant to this team role"),
    )

    notes = models.TextField(
        blank=True,
        verbose_name=_("Membership Notes"),
        help_text=_("Additional notes about this team membership"),
    )

    class Meta:
        verbose_name = _("Team Membership")
        verbose_name_plural = _("Team Memberships")
        db_table = "team_memberships"
        unique_together = ("person", "team")
        ordering = ["team", "-is_primary_team", "role", "person"]
        indexes = [
            models.Index(fields=["person", "team"]),
            # models.Index(fields=["role"]),
            models.Index(fields=["status"]),
            models.Index(fields=["is_primary_team"]),
            models.Index(fields=["date_joined"]),
        ]

    panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("person"),
                        FieldPanel("team"),
                    ]
                ),
            ],
            heading=_("Basic Information"),
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("status"),
                    ]
                ),
                FieldRowPanel(
                    [
                        FieldPanel("date_joined"),
                        FieldPanel("date_left"),
                    ]
                ),
                FieldRowPanel(
                    [
                        FieldPanel("is_primary_team"),
                        FieldPanel("allocation_percentage"),
                    ]
                ),
            ],
            heading=_("Membership Details"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("responsibilities"),
                FieldPanel("skills"),
                FieldPanel("notes"),
            ],
            heading=_("Role & Responsibilities"),
        ),
    ]

    search_fields = [
        index.SearchField("responsibilities"),
        index.SearchField("notes"),
        index.RelatedFields(
            "person",
            [
                index.SearchField("full_name"),
                index.SearchField("email"),
            ],
        ),
        # index.FilterField("role"),
        index.FilterField("status"),
    ]

    # ======================
    # PROPERTIES
    # ======================

    @property
    def is_active_member(self):
        """Check if membership is currently active."""
        return self.status == self.MembershipStatus.ACTIVE

    @property
    def duration_days(self):
        """Calculate membership duration in days."""
        end_date = self.date_left or timezone.now().date()
        return (end_date - self.date_joined).days

    @property
    def duration_display(self):
        """Get human-readable membership duration."""
        days = self.duration_days
        if days >= 365:
            years = days // 365
            return f"{years} year{'s' if years > 1 else ''}"
        elif days >= 30:
            months = days // 30
            return f"{months} month{'s' if months > 1 else ''}"
        return f"{days} day{'s' if days > 1 else ''}"

    # ======================
    # METHODS
    # ======================

    def clean(self):
        """Validate membership data."""
        super().clean()

        # Validate allocation percentage
        if self.allocation_percentage > 100:
            raise ValidationError(
                {"allocation_percentage": _("Allocation percentage cannot exceed 100%.")}
            )

        # Validate date consistency
        if self.date_left and self.date_left < self.date_joined:
            raise ValidationError({"date_left": _("Leave date cannot be before join date.")})

    def save(self, *args, **kwargs):
        """Handle membership status and team leader updates."""
        # Auto-set status based on dates
        if self.date_left and self.date_left <= timezone.now().date():
            self.status = self.MembershipStatus.INACTIVE

        # Ensure only one primary team per person
        if self.is_primary_team and self.person:
            TeamMembership.objects.filter(person=self.person, is_primary_team=True).exclude(
                pk=self.pk
            ).update(is_primary_team=False)

        super().save(*args, **kwargs)

    def activate(self):
        """Activate membership."""
        self.status = self.MembershipStatus.ACTIVE
        self.date_left = None
        self.save()

    def deactivate(self, leave_date=None):
        """Deactivate membership."""
        self.status = self.MembershipStatus.INACTIVE
        self.date_left = leave_date or timezone.now().date()
        self.save()

    def __str__(self):
        return f"{self.person.full_name} - {self.team.name}"


# -------------------------------------------------------------------
# TEAM MODEL
# -------------------------------------------------------------------
class Team(DefaultBase, ClusterableModel):
    """
    Enhanced Team model within a department with comprehensive team management features.
    """

    class TeamType(models.TextChoices):
        DEPARTMENTAL = "departmental", _("Departmental Team")
        PROJECT = "project", _("Project Team")
        CROSS_FUNCTIONAL = "cross_functional", _("Cross-functional Team")
        TASK_FORCE = "task_force", _("Task Force")
        COMMITTEE = "committee", _("Committee")
        COMMUNITY = "community", _("Community of Practice")
        INNOVATION = "innovation", _("Innovation Team")
        OPERATIONAL = "operational", _("Operational Team")

    class TeamStatus(models.TextChoices):
        ACTIVE = "active", _("Active")
        PLANNING = "planning", _("In Planning")
        ON_HOLD = "on_hold", _("On Hold")
        COMPLETED = "completed", _("Completed")
        ARCHIVED = "archived", _("Archived")

    # Basic Information
    name = models.CharField(
        max_length=100, verbose_name=_("Team Name"), help_text=_("Official name of the team")
    )

    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name=_("Slug"),
        help_text=_("URL-friendly version of the team name"),
    )

    short_name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Short Name"),
        help_text=_("Abbreviated name for display in tight spaces"),
    )

    # Categorization
    team_type = models.CharField(
        max_length=20,
        choices=TeamType.choices,
        default=TeamType.DEPARTMENTAL,
        verbose_name=_("Team Type"),
        help_text=_("Type of team and its primary purpose"),
    )

    status = models.CharField(
        max_length=20,
        choices=TeamStatus.choices,
        default=TeamStatus.ACTIVE,
        verbose_name=_("Team Status"),
        help_text=_("Current operational status of the team"),
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="teams",
        verbose_name=_("Parent Department"),
        help_text=_("Department that this team belongs to"),
    )


    # Team Details
    purpose = models.TextField(
        blank=True,
        verbose_name=_("Team Purpose"),
        help_text=_("Primary purpose and mission of the team"),
    )

    objectives = models.TextField(
        blank=True,
        verbose_name=_("Key Objectives"),
        help_text=_("Main objectives and goals for the team"),
    )

    success_metrics = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Success Metrics"),
        help_text=_("Key metrics to measure team success"),
    )

    meeting_schedule = models.TextField(
        blank=True,
        verbose_name=_("Meeting Schedule"),
        help_text=_("Regular meeting days, times, and frequency"),
    )

    # Visual Identity
    color = models.CharField(
        max_length=7,
        blank=True,
        default="#3B82F6",
        verbose_name=_("Team Color"),
        help_text=_("Team color in hex format for visual identification"),
    )

    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Team Icon"),
        help_text=_("Icon class name for team visual representation"),
    )

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Team Image"),
        help_text=_("Team photo or representative image"),
    )

    leader = models.ForeignKey(
        getattr(settings, 'PROFILE_MODEL', 'auth.User'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="led_teams",
        verbose_name=_("Team Leader"),
        help_text=_("Main person responsible for this team"),
    )

    deputy_leader = models.ForeignKey(
        getattr(settings, 'PROFILE_MODEL', 'auth.User'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deputy_led_teams",
        verbose_name=_("Deputy Leader"),
        help_text=_("Secondary person responsible for this team"),
    )

    # Settings
    max_members = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Maximum Members"),
        help_text=_("Maximum number of team members allowed"),
    )

    requires_approval = models.BooleanField(
        default=False,
        verbose_name=_("Requires Approval"),
        help_text=_("New members require approval to join"),
    )

    is_visible = models.BooleanField(
        default=True,
        verbose_name=_("Visible to Organization"),
        help_text=_("Team is visible to other organization members"),
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Display Order"),
        help_text=_("Order in which teams are displayed"),
    )

    # Analytics
    member_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name=_("Member Count"),
        help_text=_("Current number of active team members"),
    )

    active_since = models.DateField(
        default=timezone.now,
        verbose_name=_("Active Since"),
        help_text=_("Date when team became active"),
    )

    last_activity = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Last Activity"),
        help_text=_("When the team was last active"),
    )

    class Meta:
        verbose_name = _("Team")
        verbose_name_plural = _("Teams")
        db_table = "teams"
        ordering = ["department", "display_order", "name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["name"]),
            models.Index(fields=["department"]),
            models.Index(fields=["team_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["display_order"]),
            models.Index(fields=["active_since"]),
        ]

    search_fields = [
        index.SearchField("name", boost=2),
        index.SearchField("short_name", boost=2),
        index.SearchField("purpose"),
        index.SearchField("objectives"),
        index.FilterField("department"),
        index.FilterField("team_type"),
        index.FilterField("status"),
        index.FilterField("is_active"),
        index.RelatedFields(
            "memberships__person",
            [
                index.SearchField("full_name"),
            ],
        ),
    ]

    panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("name"),
                        FieldPanel("short_name"),
                    ]
                ),
                FieldPanel("slug"),
                FieldRowPanel(
                    [
                        FieldPanel("team_type"),
                        FieldPanel("status"),
                    ]
                ),
                FieldPanel("department"),
            ],
            heading=_("Basic Information"),
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("leader"),
                        FieldPanel("deputy_leader"),
                    ]
                ),
            ],
            heading=_("Leadership"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("purpose"),
                FieldPanel("objectives"),
                FieldPanel("success_metrics"),
                FieldPanel("meeting_schedule"),
            ],
            heading=_("Team Details"),
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("color"),
                        FieldPanel("icon"),
                    ]
                ),
                FieldPanel("image"),
            ],
            heading=_("Visual Identity"),
        ),
        MultiFieldPanel(
            [
                InlinePanel(
                    "memberships", label=_("Team Members"), heading=_("Team Membership Management")
                ),
            ],
            heading=_("Members"),
        ),
        MultiFieldPanel(
            [],
            heading=_("Tagging & Categorization"),
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("max_members"),
                        FieldPanel("requires_approval"),
                        FieldPanel("is_visible"),
                    ]
                ),
                FieldPanel("display_order"),
            ],
            heading=_("Settings"),
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("member_count", read_only=True),
                        FieldPanel("active_since"),
                        FieldPanel("last_activity", read_only=True),
                    ]
                ),
            ],
            heading=_("Analytics"),
            classname="collapsible collapsed",
        ),
    ]

    # ======================
    # PROPERTIES
    # ======================

    @property
    def active_members(self):
        """Get active team members."""
        return self.memberships.filter(status=TeamMembership.MembershipStatus.ACTIVE)

    @property
    def active_member_count(self):
        """Get count of active members."""
        return self.active_members.count()

    @property
    def is_full(self):
        """Check if team has reached maximum capacity."""
        if self.max_members:
            return self.active_member_count >= self.max_members
        return False

    @property
    def available_slots(self):
        """Calculate available member slots."""
        if self.max_members:
            return max(0, self.max_members - self.active_member_count)
        return None

    @property
    def duration_days(self):
        """Calculate team duration in days."""
        return (timezone.now().date() - self.active_since).days

    @property
    def is_operational(self):
        """Check if team is operational."""
        return self.status == self.TeamStatus.ACTIVE

    # ======================
    # METHODS
    # ======================

    def clean(self):
        """Validate team data."""
        super().clean()

        # Validate leader consistency
        if self.leader and self.leader.type != "EMP":
            raise ValidationError({"leader": _("Team leader must be an employee.")})

        if self.deputy_leader and self.deputy_leader.type != "EMP":
            raise ValidationError({"deputy_leader": _("Deputy leader must be an employee.")})

        # Validate member count
        if self.max_members and self.active_member_count > self.max_members:
            raise ValidationError(
                {"max_members": _("Team has more active members than the maximum allowed.")}
            )

    def save(self, *args, **kwargs):
        """Auto-update member count and handle team status."""
        # Auto-set code prefix
        self.code_prefix = "TEM"

        # Update member count
        self.member_count = self.active_member_count

        # Update last activity
        if self.member_count > 0:
            self.last_activity = timezone.now()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Get URL for team detail page."""
        return reverse("team-detail", kwargs={"slug": self.slug})

    def add_member(self, person, role=TeamMembership.MemberRole.MEMBER, **kwargs):
        """Add a member to the team."""
        if self.is_full:
            raise ValidationError(_("Team has reached maximum capacity."))

        membership, created = TeamMembership.objects.get_or_create(
            person=person, team=self, defaults={"role": role, **kwargs}
        )

        if not created:
            membership.role = role
            for key, value in kwargs.items():
                setattr(membership, key, value)
            membership.save()

        return membership

    def remove_member(self, person, leave_date=None):
        """Remove a member from the team."""
        try:
            membership = TeamMembership.objects.get(person=person, team=self)
            membership.deactivate(leave_date)
            return True
        except TeamMembership.DoesNotExist:
            return False

    def get_member_roles(self):
        """Get distribution of member roles."""
        from django.db.models import Count

        return (
            self.memberships.filter(status=TeamMembership.MembershipStatus.ACTIVE)
            .values("role")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

    def can_join(self, person):
        """Check if a person can join this team."""
        if not self.is_operational:
            return False, _("Team is not currently operational.")

        if self.is_full:
            return False, _("Team has reached maximum capacity.")

        if self.memberships.filter(
            person=person, status=TeamMembership.MembershipStatus.ACTIVE
        ).exists():
            return False, _("Person is already a team member.")

        return True, _("Can join team.")

    def update_activity(self):
        """Update team's last activity timestamp."""
        self.last_activity = timezone.now()
        self.save(update_fields=["last_activity"])

    def __str__(self):
        return f"{self.name} ({self.department.name})"


# -------------------------------------------------------------------
# TEAM INVITATION MODEL
# -------------------------------------------------------------------
class TeamInvitation(DefaultBase):
    """
    Team invitation system for managing member invitations.
    """

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="invitations")

    email = models.EmailField(verbose_name=_("Invitee Email"))
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_team_invitations"
    )
    role = models.CharField(
        max_length=20,
        choices=TeamMembership.MemberRole.choices,
        default=TeamMembership.MemberRole.MEMBER,
    )
    token = models.CharField(max_length=100, unique=True)
    expires_at = models.DateTimeField()
    is_accepted = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("Team Invitation")
        verbose_name_plural = _("Team Invitations")
        ordering = ["-created_at"]

    def __str__(self):
        status = "Accepted" if self.is_accepted else "Pending"
        return f"Invitation: {self.email} -> {self.team.name} ({status})"

    def is_expired(self):
        """Check if invitation has expired."""
        return timezone.now() > self.expires_at

    def accept(self, person):
        """Accept the invitation."""
        if self.is_expired():
            raise ValidationError(_("Invitation has expired."))

        if self.is_accepted:
            raise ValidationError(_("Invitation has already been accepted."))

        # Add person to team
        self.team.add_member(person, role=self.role)

        self.is_accepted = True
        self.accepted_at = timezone.now()
        self.save()
