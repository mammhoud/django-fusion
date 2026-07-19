"""
Management command: send_error_report
======================================
Collects error-page hits (4xx/5xx) logged in the last hour and
emails a structured HTML report to the development team.

Schedule via cron (inside container or host):
    0 * * * *  cd /app && python com send_error_report

Usage:
    python com send_error_report [--hours 1] [--to email@example.com]
"""

import logging
from datetime import timedelta

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.utils import timezone

logger = logging.getLogger(__name__)

# ── Recipients ────────────────────────────────────────────────────────────────
DEV_TEAM_EMAIL = "ctc-research@gmail.com"


class Command(BaseCommand):
    help = "Send hourly error-page report to the development team"

    def add_arguments(self, parser):
        parser.add_argument(
            "--hours",
            type=int,
            default=1,
            help="Look-back window in hours (default: 1)",
        )
        parser.add_argument(
            "--to",
            type=str,
            default=DEV_TEAM_EMAIL,
            help="Recipient email address",
        )

    def handle(self, *args, **options):
        hours = options["hours"]
        recipient = options["to"]
        since = timezone.now() - timedelta(hours=hours)

        errors = self._collect_errors(since)

        if not errors:
            self.stdout.write(self.style.SUCCESS(
                f"✅ No errors in the last {hours}h — no report sent."
            ))
            return

        subject, html_body, text_body = self._build_email(errors, since, hours)
        self._send(subject, html_body, text_body, recipient)
        self.stdout.write(self.style.SUCCESS(
            f"📧 Error report sent to {recipient} ({len(errors)} entries)"
        ))

    # ── Data collection ────────────────────────────────────────────────────────

    def _collect_errors(self, since):
        """
        Pull error records from every available source:
          1. django.request logger entries stored in DB (if django-db-logger is installed)
          2. Wagtail admin log (wagtail.log_action)
          3. Plain log file scan (fallback)
        Returns a list of dicts with keys: timestamp, level, path, status, message.
        """
        errors = []

        # ── Source 1: django-db-logger (optional) ─────────────────────────────
        try:
            from django_db_logger.models import StatusLog  # type: ignore
            qs = StatusLog.objects.filter(
                create_datetime__gte=since,
                level_no__gte=logging.ERROR,
            ).order_by("-create_datetime")[:200]
            for entry in qs:
                errors.append({
                    "timestamp": entry.create_datetime,
                    "level": entry.get_level_no_display(),
                    "path": getattr(entry, "pathname", "—"),
                    "status": "—",
                    "message": entry.msg[:500],
                    "traceback": getattr(entry, "trace", "") or "",
                })
        except Exception:
            pass

        # ── Source 2: Wagtail log (page-not-found / server-error actions) ─────
        try:
            from wagtail.log_actions import registry as log_registry  # noqa
            from wagtail.models import PageLogEntry
            qs = PageLogEntry.objects.filter(
                timestamp__gte=since,
                action__in=["wagtail.page_unpublish", "wagtail.delete"],
            ).select_related("page").order_by("-timestamp")[:50]
            for entry in qs:
                errors.append({
                    "timestamp": entry.timestamp,
                    "level": "WARNING",
                    "path": getattr(entry.page, "url_path", "—") if entry.page else "—",
                    "status": entry.action,
                    "message": f"Wagtail action: {entry.action} on '{entry.page}'",
                    "traceback": "",
                })
        except Exception:
            pass

        # ── Source 3: Log file scan (fallback) ────────────────────────────────
        if not errors:
            errors.extend(self._scan_log_files(since))

        return errors

    def _scan_log_files(self, since):
        """Scan log files under logs/ for ERROR/CRITICAL lines."""
        import os
        import re

        errors = []
        log_dir = getattr(settings, "LOG_DIR", None) or "/app/logs"
        if not os.path.isdir(log_dir):
            return errors

        ts_pattern = re.compile(
            r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})"
        )
        level_pattern = re.compile(r"\b(ERROR|CRITICAL)\b")

        for fname in os.listdir(log_dir):
            if not fname.endswith(".log"):
                continue
            fpath = os.path.join(log_dir, fname)
            try:
                with open(fpath, "r", errors="replace") as fh:
                    for line in fh:
                        if not level_pattern.search(line):
                            continue
                        m = ts_pattern.search(line)
                        if not m:
                            continue
                        try:
                            from django.utils.dateparse import parse_datetime
                            ts = parse_datetime(m.group(1).replace(" ", "T"))
                            if ts and timezone.is_naive(ts):
                                ts = timezone.make_aware(ts)
                            if ts and ts < since:
                                continue
                        except Exception:
                            pass
                        errors.append({
                            "timestamp": m.group(1),
                            "level": level_pattern.search(line).group(1),
                            "path": fname,
                            "status": "—",
                            "message": line.strip()[:500],
                            "traceback": "",
                        })
            except OSError:
                continue

        return errors[:200]

    # ── Email builder ──────────────────────────────────────────────────────────

    def _build_email(self, errors, since, hours):
        from django.template.loader import render_to_string

        site_name = getattr(settings, "WAGTAIL_SITE_NAME", "CTC Hub")
        now = timezone.now()
        subject = (
            f"[{site_name}] ⚠️ Error Report — "
            f"{len(errors)} error(s) in the last {hours}h "
            f"({now.strftime('%Y-%m-%d %H:%M')} UTC)"
        )

        # Format timestamps for display
        for e in errors:
            ts = e["timestamp"]
            e["timestamp"] = ts.strftime("%Y-%m-%d %H:%M:%S") if hasattr(ts, "strftime") else str(ts)

        context = {
            "site_name": site_name,
            "since": since.strftime("%Y-%m-%d %H:%M"),
            "now": now.strftime("%Y-%m-%d %H:%M"),
            "error_count": len(errors),
            "errors": errors,
        }

        html_body = render_to_string("emails/error_report.html", context)

        rows_text = ""
        for i, e in enumerate(errors, 1):
            rows_text += f"\n[{i}] {e['timestamp']} | {e['level']} | {e['path']} | {e['status']}\n    {e['message']}\n"

        text_body = (
            f"{site_name} — Error Report\n"
            f"Period: {since.strftime('%Y-%m-%d %H:%M')} → {now.strftime('%Y-%m-%d %H:%M')} UTC\n"
            f"Total errors: {len(errors)}\n"
            f"{'='*60}{rows_text}"
        )

        return subject, html_body, text_body

    # ── Sender ─────────────────────────────────────────────────────────────────

    def _send(self, subject, html_body, text_body, recipient):
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@ctc-research.com")
        msg = EmailMultiAlternatives(subject, text_body, from_email, [recipient])
        msg.attach_alternative(html_body, "text/html")
        try:
            msg.send()
        except Exception as exc:
            logger.error(f"[ErrorReport] Failed to send report: {exc}", exc_info=True)
            self.stderr.write(self.style.ERROR(f"❌ Email send failed: {exc}"))
            raise
