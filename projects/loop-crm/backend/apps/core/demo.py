"""Demo dataset provisioning for Loop-CRM.

``seed_workspace`` fills a workspace with the complete product trail —
pipeline and deals, campaign and scheduled posts, plus the
won-deal-to-invoice revenue trail and attributed touchpoints — so a fresh
"Start free" signup sees a living product the moment they sign in.
Idempotent per workspace: rerunning keeps existing records and adds nothing
new.

Two entry points share this module:
* ``python manage.py seed_demo`` (demo workspace + accounts), and
* the allauth ``user_signed_up`` signal, which provisions the new user's
  personal workspace straight from the landing's Start free flow.
"""
from __future__ import annotations

from decimal import Decimal

from django.utils import timezone

from apps.attribution.models import AttributionModel, AttributionTouchpoint
from apps.core.models import UserProfile, Workspace
from apps.crm.models import Company, Contact, Deal, Pipeline, PipelineStage
from apps.finance.models import Invoice, Payment, RevenueEvent
from apps.marketing.models import Campaign, Post, PostAnalytics, SocialChannel

STAGES = [
    ("Lead", "lead", "#d9b26c", 10),
    ("Qualified", "qualified", "#7fb4d9", 30),
    ("Proposal", "proposal", "#b28cd9", 55),
    ("Negotiation", "negotiation", "#e0a35c", 80),
    ("Closed Won", "closed_won", "#8bcbb5", 100),
]

COMPANIES = [
    ("Halcyon Labs", "Developer Tools", "San Francisco", 2400000),
    ("Northwind", "Logistics", "Chicago", 900000),
    ("Sable & Co", "Design Studio", "New York", 420000),
    ("Meadowbank", "AgriTech", "Des Moines", 780000),
    ("Copperline", "Fintech", "Austin", 1600000),
    ("Fieldstone", "Construction", "Denver", 650000),
    ("Aurelia Health", "Healthcare", "Boston", 3100000),
    ("Bluepeak", "Consumer SaaS", "Seattle", 1200000),
]

CONTACTS = [
    ("Priya", "Raghunathan", "Head of RevOps", "Halcyon Labs"),
    ("Tomás", "Rivera", "VP Sales", "Northwind"),
    ("Yuki", "Tanaka", "Founder", "Sable & Co"),
    ("Amara", "Okafor", "CRO", "Meadowbank"),
    ("Jonas", "Lindqvist", "Growth Lead", "Copperline"),
    ("Elena", "Marks", "Operations Director", "Fieldstone"),
    ("Sofia", "Bennett", "CMO", "Aurelia Health"),
    ("Marco", "Delgado", "Head of Partnerships", "Bluepeak"),
]

DEAL_SEED = [
    ("Enterprise rollout", "Halcyon Labs", 125000, "closed_won", 24),
    ("Platform expansion", "Aurelia Health", 88000, "closed_won", 12),
    ("Team plan", "Northwind", 24000, "negotiation", 8),
    ("Design retainer", "Sable & Co", 15000, "proposal", 6),
    ("Pilot program", "Meadowbank", 31000, "proposal", 4),
    ("API migration", "Copperline", 57000, "qualified", 2),
    ("Fleet rollout", "Fieldstone", 42000, "qualified", 1),
    ("Growth plan", "Bluepeak", 66000, "lead", 0),
]

POST_SEED = [
    ("Launch teaser: the revenue loop is open.", "linkedin", "published", -6, "urn:li:share:launch-teaser"),
    ("Thread: why attribution belongs inside the CRM.", "twitter", "published", -4, "tweet-20931"),
    ("Case study preview: Halcyon Labs closes 2.4x faster.", "linkedin", "scheduled", 3, ""),
    ("The 4 steps to revenue attribution, explained.", "twitter", "scheduled", 5, ""),
    ("Waitlist opens for the finance ledger.", "linkedin", "approved", 7, ""),
    ("Draft: pricing announcement for Pro.", "twitter", "draft", 9, ""),
    ("Draft: webinar on multi-touch attribution.", "linkedin", "pending_approval", 11, ""),
]


def seed_workspace(workspace: Workspace, owner) -> dict[str, int]:
    """Create (or keep) the demo dataset for a workspace; returns entity counts.

    ``owner`` is the user recorded as the creator/owner of every record, so a
    fresh Start free account owns the demo data in its own workspace.
    """
    today = timezone.localdate()
    counts: dict[str, int] = {}

    # ── Pipeline + stages ───────────────────────────────────────────────
    pipeline, _ = Pipeline.objects.get_or_create(
        workspace=workspace, name="Sales pipeline", defaults={"is_default": True, "order": 0}
    )
    stage_map: dict[str, PipelineStage] = {}
    for order, (name, stage_type, color, probability) in enumerate(STAGES):
        stage, _ = PipelineStage.objects.get_or_create(
            pipeline=pipeline, name=name,
            defaults={"stage_type": stage_type, "color": color, "probability": probability, "order": order},
        )
        stage_map[stage_type] = stage
    counts["pipelines"] = 1

    # ── Campaign + channels ─────────────────────────────────────────────
    campaign, _ = Campaign.objects.get_or_create(
        workspace=workspace,
        name="Summer Launch 2026",
        defaults={
            "description": "Product launch campaign across LinkedIn and X with attribution.",
            "start_date": today.replace(month=6, day=1),
            "end_date": today.replace(month=8, day=31),
            "budget": Decimal("45000.00"),
            "owner": owner,
        },
    )
    SocialChannel.objects.get_or_create(
        workspace=workspace, platform="linkedin", account_name="urn:li:organization:loopcrm"
    )
    SocialChannel.objects.get_or_create(workspace=workspace, platform="twitter", account_name="@loopcrm")
    counts["campaigns"] = 1
    counts["channels"] = 2

    # ── Companies, contacts, deals ──────────────────────────────────────
    company_map: dict[str, Company] = {}
    contact_map: dict[str, Contact] = {}
    for name, industry, city, revenue in COMPANIES:
        company, _ = Company.objects.get_or_create(
            workspace=workspace, name=name,
            defaults={"industry": industry, "city": city, "annual_revenue": Decimal(revenue), "owner": owner},
        )
        company_map[name] = company

    for first, last, title, company_name in CONTACTS:
        contact, _ = Contact.objects.get_or_create(
            workspace=workspace, company=company_map[company_name], email=f"{first.lower()}.{last.lower()}@example.com",
            defaults={"first_name": first, "last_name": last, "title": title, "owner": owner},
        )
        contact_map[company_name] = contact

    deal_map: dict[str, Deal] = {}
    for name, company_name, value, stage_type, days_out in DEAL_SEED:
        deal, _ = Deal.objects.get_or_create(
            workspace=workspace, name=name, company=company_map[company_name],
            defaults={
                "contact": contact_map[company_name],
                "value": Decimal(value),
                "pipeline": pipeline,
                "stage": stage_map[stage_type],
                "expected_close_date": today + timezone.timedelta(days=days_out),
                "owner": owner,
                "campaign": campaign if stage_type in {"closed_won", "negotiation", "proposal", "qualified"} else None,
            },
        )
        deal_map[name] = deal
    counts["companies"] = len(company_map)
    counts["contacts"] = len(contact_map)
    counts["deals"] = len(deal_map)

    # ── Posts (lifecycle showcase) ──────────────────────────────────────
    channel_by_platform = {
        "linkedin": SocialChannel.objects.get(workspace=workspace, platform="linkedin", account_name="urn:li:organization:loopcrm"),
        "twitter": SocialChannel.objects.get(workspace=workspace, platform="twitter", account_name="@loopcrm"),
    }
    post_map: dict[str, Post] = {}
    for content, platform, status, days_out, external_id in POST_SEED:
        post, _ = Post.objects.get_or_create(
            workspace=workspace, channel=channel_by_platform[platform], content=content,
            defaults={
                "campaign": campaign,
                "scheduled_at": timezone.now() + timezone.timedelta(days=days_out, hours=10),
                "status": status,
                "external_id": external_id,
                "created_by": owner,
            },
        )
        post_map[content] = post

    published = next((p for p in post_map.values() if p.status == "published"), None)
    if published and not hasattr(published, "analytics"):
        PostAnalytics.objects.create(post=published, impressions=18400, clicks=940, likes=610, comments=88, shares=142)
    counts["posts"] = len(post_map)

    # ── Finance trail for a won deal ────────────────────────────────────
    won_deal = deal_map["Enterprise rollout"]
    invoice, _ = Invoice.objects.get_or_create(
        workspace=workspace, number="INV-2026-014",
        defaults={
            "company": won_deal.company,
            "contact": won_deal.contact,
            "deal": won_deal,
            "status": "paid",
            "issued_on": today - timezone.timedelta(days=10),
            "due_on": today + timezone.timedelta(days=20),
            "subtotal": won_deal.value,
            "tax": Decimal("0.00"),
            "notes": "Created automatically by the deal-won workflow.",
            "created_by": owner,
        },
    )
    Payment.objects.get_or_create(
        workspace=workspace, invoice=invoice, amount=won_deal.value,
        defaults={"method": "bank_transfer", "reference": "PAY-2026-031", "created_by": owner},
    )
    RevenueEvent.objects.get_or_create(
        workspace=workspace, deal=won_deal,
        defaults={
            "campaign": campaign,
            "invoice": invoice,
            "kind": "deal_won",
            "amount": won_deal.value,
            "recognized_on": today - timezone.timedelta(days=10),
            "metadata": {"source": "seed_demo", "model": "linear"},
        },
    )
    counts["finance"] = 3  # invoice, payment, revenue event

    # ── Attribution ─────────────────────────────────────────────────────
    AttributionModel.objects.get_or_create(
        workspace=workspace, name="Linear", defaults={"model_type": "linear", "is_active": True}
    )
    attribution_posts = [
        post_map["Launch teaser: the revenue loop is open."],
        post_map["Thread: why attribution belongs inside the CRM."],
    ]
    if not AttributionTouchpoint.objects.filter(deal=won_deal).exists():
        for i, post in enumerate(attribution_posts):
            AttributionTouchpoint.objects.create(
                workspace=workspace,
                deal=won_deal,
                post=post,
                campaign=campaign,
                source="post",
                occurred_at=timezone.now() - timezone.timedelta(days=20 - i * 3),
                weight=Decimal("0.5"),
            )
    counts["touchpoints"] = 2

    return counts


# Demo account contract — single source of truth shared by seed_demo, the
# login-page demo panel, and the container entrypoint.
DEMO_WORKSPACE_SLUG = "demo-workspace"
DEMO_EMAIL = "demo@loop.dev"
DEMO_PASSWORD = "demo-pass-123"

DEMO_MEMBERS = [
    ("sales", "Sales Manager", "sales_manager"),
    ("marketing", "Marketing Manager", "marketing_manager"),
    ("revops", "RevOps Manager", "revops_manager"),
]


def ensure_user_workspace(user) -> Workspace:
    """Give a user a personal workspace and seed it with the demo dataset.

    Used by the Start free signup flow and by ``seed_demo --user``. The user
    owns every seeded record; an existing workspace is seeded in place.
    """
    profile, _ = UserProfile.objects.get_or_create(user=user)
    if profile.workspace_id is None:
        workspace = Workspace.objects.create(name=f"{user}'s workspace", slug=f"demo-{user.pk}")
        profile.workspace = workspace
        profile.role = "super_admin"
        profile.save(update_fields=["workspace", "role"])
    else:
        workspace = profile.workspace
    seed_workspace(workspace, owner=user)
    return workspace
