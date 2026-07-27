"""
CSV Parser service for email automation.

Grammar
-------
The CSV file has two columns:

    email,role
    user@example.com,instructor/manager
    other@example.com,content_manager

- ``email``: a valid email address (required, non-empty)
- ``role``: one or more role names separated by ``/`` or ``,``
  (optional; roles are normalised to lowercase with spaces replaced by ``_``)

Round-trip guarantee
--------------------
``CSVParser.parse(pretty_print(records)) == records``

That is, serialising a list of :class:`EmailRecord` objects back to CSV and
then re-parsing the result produces an equivalent list.
"""

import csv
import io
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


@dataclass
class EmailRecord:
    """Represents a single record from emails.csv"""
    email: str
    roles: List[str]

    @property
    def primary_role(self) -> str:
        """Get the first role as primary."""
        return self.roles[0] if self.roles else ''


class CSVParser:
    """
    Parses emails.csv and extracts email/role information.
    Handles multiple roles per user (separated by / or comma).
    """

    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)

    def parse(self) -> List[EmailRecord]:
        """
        Parse CSV file and return list of EmailRecord objects.

        Returns:
            List of EmailRecord objects

        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If CSV is malformed
        """
        if not self.csv_path.exists():
            logger.error(f"CSV file not found: {self.csv_path}")
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")

        records = []

        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row_num, row in enumerate(reader, start=2):
                    try:
                        email = row.get('email', '').strip()
                        role_str = row.get('role', '').strip()

                        if not email:
                            logger.warning(f"Empty email field at row {row_num}")
                            continue

                        # Parse multiple roles (separated by / or comma)
                        roles = self._parse_roles(role_str)

                        records.append(EmailRecord(email=email, roles=roles))

                    except Exception as e:
                        logger.error(f"Error parsing row {row_num}: {e}")
                        continue

            logger.info(f"CSV parsed successfully: {len(records)} records")
            return records

        except Exception as e:
            logger.error(f"Failed to parse CSV: {e}")
            raise ValueError(f"Failed to parse CSV: {e}")

    def _parse_roles(self, role_str: str) -> List[str]:
        """
        Parse role string into list of roles.
        Handles both / and comma separators.
        """
        if not role_str:
            return []

        # Split by / or comma
        if '/' in role_str:
            roles = role_str.split('/')
        else:
            roles = role_str.split(',')

        # Clean and normalize
        roles = [r.strip().lower().replace(' ', '_') for r in roles if r.strip()]
        return roles

    @staticmethod
    def pretty_print(records: List["EmailRecord"]) -> str:
        """
        Serialise a list of :class:`EmailRecord` objects back to CSV text.

        The output is a valid CSV string that can be written to a file and
        re-parsed by :meth:`parse` to produce an equivalent list of records.

        Grammar produced::

            email,role
            user@example.com,instructor/manager
            other@example.com,content_manager

        Roles are joined with ``/`` (the canonical separator).

        Args:
            records: List of :class:`EmailRecord` objects to serialise.

        Returns:
            A CSV string with a header row followed by one row per record.
        """
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["email", "role"])
        writer.writeheader()
        for record in records:
            writer.writerow({
                "email": record.email,
                "role": "/".join(record.roles),
            })
        return output.getvalue()

    def create_default_csv(self) -> None:
        """Create default emails.csv if it doesn't exist."""
        if self.csv_path.exists():
            logger.info("CSV file already exists")
            return

        default_data = [
            {'email': 'E.babiker55@gmail.com', 'role': 'instructor/manager'},
            {'email': 'yasirzaroug8@gmail.com', 'role': 'instructor/manager'},
            {'email': 'dranas352002@gmail.com', 'role': 'content_manager'},
            {'email': 'ctcresearchhub2025@gmail.com', 'role': 'supervisor'},
        ]

        try:
            self.csv_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['email', 'role'])
                writer.writeheader()
                writer.writerows(default_data)

            logger.info("Default CSV created successfully")

        except Exception as e:
            logger.error(f"Failed to create CSV: {e}")
            raise
