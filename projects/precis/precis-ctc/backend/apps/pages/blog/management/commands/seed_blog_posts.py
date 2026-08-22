"""Seed the CTC Research editorial blog — categories, tags, and published posts.

The blog API (``/api/blog/``) is the frontend's source for the /blog/ index
and detail routes. Without published rows the Astro shell renders an error
fallback, so this command creates the seeded editorial set. It is idempotent:
existing slugs are left untouched and missing rows are created.

Usage::

    python manage.py seed_blog_posts

"""

from datetime import datetime, timedelta, timezone

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.timezone import now

from apps.pages.blog.models.category import BlogCategory
from apps.pages.blog.models.post import BlogPost
from apps.pages.blog.models.tag import BlogTag

# ── Editorial seed — one authoritative definition of the blog's content ──────
# Each entry: title, slug, category, tags, excerpt, and body (Wagtail rich text).
CATEGORIES = [
    {"name": "Research Methods", "slug": "research-methods"},
    {"name": "Medical AI", "slug": "medical-ai"},
    {"name": "Evidence Synthesis", "slug": "evidence-synthesis"},
    {"name": "Scientific Writing", "slug": "scientific-writing"},
]

TAGS = [
    {"name": "Protocols", "slug": "protocols"},
    {"name": "Publication", "slug": "publication"},
    {"name": "Machine Learning", "slug": "machine-learning"},
    {"name": "Clinical Evidence", "slug": "clinical-evidence"},
    {"name": "Systematic Review", "slug": "systematic-review"},
    {"name": "GRADE", "slug": "grade"},
    {"name": "Manuscript", "slug": "manuscript"},
    {"name": "Peer Review", "slug": "peer-review"},
]

POSTS = [
    {
        "title": "From Protocol to Publication: The Research Lifecycle in Practice",
        "slug": "from-protocol-to-publication-research-lifecycle",
        "category": "research-methods",
        "tags": ["protocols", "publication"],
        "excerpt": (
            "A practical walk through the full research lifecycle — question, "
            "protocol, registration, data, analysis, manuscript, and peer "
            "review — and the quality controls that protect each stage."
        ),
        "days_ago": 21,
        "body": """
            <h2>Every strong study starts with a written question</h2>
            <p>A research question that cannot be written down precisely cannot be
            answered reproducibly. The protocol is the first reproducibility tool,
            not a bureaucratic form: it fixes the population, the intervention, the
            comparator, and the outcome before the data decides for you.</p>
            <h2>Registration closes the p-hacking door</h2>
            <p>Registering the analysis plan on a public registry turns the protocol
            into a contract. When the final manuscript reports the pre-specified
            endpoints — and transparently lists deviations — reviewers can trust the
            results rather than the narrative.</p>
            <h2>Publication is a service, not a finish line</h2>
            <p>Peer review works best when the manuscript answers the question the
            protocol asked. Clear methods, complete reporting checklists, and raw
            data access are what turn a study into evidence other teams can build
            on.</p>
        """,
    },
    {
        "title": "Medical AI in Clinical Evidence: Where Models Help and Where They Fall Short",
        "slug": "medical-ai-clinical-evidence-limits",
        "category": "medical-ai",
        "tags": ["machine-learning", "clinical-evidence"],
        "excerpt": (
            "Machine learning accelerates parts of the evidence pipeline — screening, "
            "extraction, coding — but it cannot manufacture validity. A guide to "
            "where models help and where they must stay out."
        ),
        "days_ago": 14,
        "body": """
            <h2>The fast parts are real</h2>
            <p>Deduplicating record sets, screening titles, and extracting structured
            fields from PDFs are genuinely faster with modern language models. Teams
            routinely cut months off systematic reviews by automating these steps —
            with a human in the loop and a disagreement log.</p>
            <h2>The slow parts are the ones that matter</h2>
            <p>Risk-of-bias judgments, outcome definitions, and clinical reasoning
            depend on context a model cannot reconstruct from text alone. When a
            model reports a pooled effect, the validity still comes from the study
            design, the population, and the measurement — not the token stream.</p>
            <h2>An evidence-first rule of thumb</h2>
            <p>Use AI to make the pipeline faster, never to make it more certain.
            Every automated claim needs a verifiable source, and every source needs
            a human reader before it enters a conclusion.</p>
        """,
    },
    {
        "title": "Writing a Systematic Review That Survives Peer Review",
        "slug": "systematic-review-peer-review-survival",
        "category": "evidence-synthesis",
        "tags": ["systematic-review", "grade"],
        "excerpt": (
            "Peer reviewers read the methods first. PRISMA reporting, a reproducible "
            "search, and GRADE-certainty language turn a good review into one that "
            "survives the round table."
        ),
        "days_ago": 7,
        "body": """
            <h2>Report the search so it can be rerun</h2>
            <p>The most common reason a review stalls at peer review is an
            unreproducible search. Report the exact databases, the full strategy,
            the date of the last run, and the number of records per source — a
            reviewer should be able to re-execute it from the text alone.</p>
            <h2>Show the decisions, not just the count</h2>
            <p>A PRISMA flow diagram documents the journey from records to included
            studies. Pair it with a reasons-for-exclusion list: reviewers need to
            see why studies were dropped, not just that they were.</p>
            <h2>Speak certainty, not certainty</h2>
            <p>GRADE separates the effect estimate from how confident we are in it.
            High certainty and low certainty can share the same point estimate —
            the difference is the language you use to present it.</p>
        """,
    },
    {
        "title": "Clarity Is a Reproducibility Tool: Precision in Scientific Writing",
        "slug": "clarity-reproducibility-scientific-writing",
        "category": "scientific-writing",
        "tags": ["manuscript", "peer-review"],
        "excerpt": (
            "Ambiguous prose produces irreproducible science. A short guide to "
            "writing methods and results that other teams can actually replicate."
        ),
        "days_ago": 2,
        "body": """
            <h2>Define every term once</h2>
            <p>If a method section uses 'significant', 'large', or 'adjusted' —
            stop and define each one. The reader should never have to infer what
            you meant from the results table.</p>
            <h2>Results report, discussion interprets</h2>
            <p>Keep the two apart. Results state what happened with the numbers and
            their uncertainty; discussion interprets, contextualizes, and admits
            limitations. Mixing them is the most common structural reason papers
            get returned for revision.</p>
            <h2>Revision is a reporting exercise</h2>
            <p>Treat reviewer comments as a reporting checklist, not a debate.
            Answer every numbered point, quote the manuscript change, and keep the
            response letter short enough that a busy editor can verify it.</p>
        """,
    },
]


class Command(BaseCommand):
    help = "Seed the CTC Research editorial blog (categories, tags, published posts)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO("⏳ Seeding editorial blog … "), ending="")
        created = {"categories": 0, "tags": 0, "posts": 0}

        for item in CATEGORIES:
            _, was_created = BlogCategory.objects.get_or_create(
                slug=item["slug"], defaults={"name": item["name"]}
            )
            created["categories"] += int(was_created)

        for item in TAGS:
            _, was_created = BlogTag.objects.get_or_create(
                slug=item["slug"], defaults={"name": item["name"]}
            )
            created["tags"] += int(was_created)

        author = self._get_author()

        for item in POSTS:
            if BlogPost.objects.filter(slug=item["slug"]).exists():
                continue
            post = BlogPost(
                title=item["title"],
                slug=item["slug"],
                author=author,
                excerpt=item["excerpt"],
                content=item["body"],
                status="published",
                published_date=now() - timedelta(days=item["days_ago"]),
                meta_description=item["excerpt"][:160],
            )
            post.save()
            post.categories.add(BlogCategory.objects.get(slug=item["category"]))
            for tag_slug in item["tags"]:
                try:
                    post.tags.add(BlogTag.objects.get(slug=tag_slug))
                except BlogTag.DoesNotExist:
                    self.stderr.write(f"  ⚠ missing tag {tag_slug!r}")
            created["posts"] += 1

        self.stdout.write(self.style.SUCCESS("done"))
        self.stdout.write(
            self.style.SUCCESS(
                f"  • Created {created['categories']} categories, {created['tags']} tags, "
                f"{created['posts']} posts (existing rows untouched)"
            )
        )

    def _get_author(self):
        """Return a stable editorial author — reuse the first staff user or the seed author."""
        User = get_user_model()
        author = (
            User.objects.filter(is_staff=True).exclude(username="").first()
            or User.objects.first()
        )
        if author is None:
            author = User.objects.create_user(
                username="ctc-editorial",
                email="editorial@ctc-research.com",
                first_name="CTC",
                last_name="Editorial",
                password=None,
            )
        return author
