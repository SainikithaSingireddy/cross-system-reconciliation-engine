import csv
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand

from reconciler.models import Location, SystemARecord, SystemBEntry


class Command(BaseCommand):
    help = "Import reconciliation CSV data"

    def normalize_reference(self, value):
        """Convert dirty references like 'REC - 1070' to 'rec1070'."""
        if not value:
            return ""

        return re.sub(r"[^a-zA-Z0-9]", "", value).lower()

    def safe_decimal(self, value):
        """Convert a CSV value to Decimal, or return None if invalid."""
        if not value or not value.strip():
            return None

        try:
            return Decimal(value.strip())
        except (InvalidOperation, ValueError):
            return None

    def safe_date(self, value):
        """Convert YYYY-MM-DD to a date, or return None."""
        if not value or not value.strip():
            return None

        from datetime import datetime

        try:
            return datetime.strptime(value.strip(), "%Y-%m-%d").date()
        except ValueError:
            return None

    def handle(self, *args, **options):
        project_root = Path(__file__).resolve().parents[4]
        data_dir = project_root / "data"

        locations_file = data_dir / "locations.csv"
        system_a_file = data_dir / "system_a.csv"
        system_b_file = data_dir / "system_b.csv"

        self.stdout.write(f"Reading data from: {data_dir}")

        
        #  Import locations
       
        location_map = {}

        with open(locations_file, newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            for row in reader:
                location_id = row["location_id"].strip()

                location, _ = Location.objects.update_or_create(
                    location_id=location_id,
                    defaults={
                        "org_id": row["org_id"].strip(),
                        "location_name": row["location_name"].strip(),
                    },
                )

                location_map[location_id] = location

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {len(location_map)} locations"
            )
        )

        
        #  Import System A
        
        a_count = 0

        with open(system_a_file, newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            for row in reader:
                location_id = row["location_id"].strip()
                location = location_map.get(location_id)

                if not location:
                    self.stdout.write(
                        self.style.WARNING(
                            f"System A row {row['record_id']}: "
                            f"unknown location {location_id}"
                        )
                    )
                    continue

                SystemARecord.objects.update_or_create(
                    record_id=row["record_id"].strip(),
                    defaults={
                        "location": location,
                        "event_date": self.safe_date(row["event_date"]),
                        "category_code": row["category_code"].strip(),
                        "actor_id": row["actor_id"].strip(),
                        "base_value": self.safe_decimal(row["base_value"]),
                        "adjustment": self.safe_decimal(row["adjustment"]),
                        "total_value": self.safe_decimal(row["total_value"]),
                        "state": row["state"].strip(),
                    },
                )

                a_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {a_count} System A records"
            )
        )

        
        #  Import System B
        
        b_count = 0

        with open(system_b_file, newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            for row in reader:
                location_id = row["location_id"].strip()
                location = location_map.get(location_id)

                if not location:
                    self.stdout.write(
                        self.style.WARNING(
                            f"System B row {row['entry_id']}: "
                            f"unknown location {location_id}"
                        )
                    )
                    continue

                SystemBEntry.objects.update_or_create(
                    entry_id=row["entry_id"].strip(),
                    defaults={
                        "record_ref": row["record_ref"].strip(),
                        "location": location,
                        "recorded_on": self.safe_date(row["recorded_on"]),
                        "value": self.safe_decimal(row["value"]),
                        "label": row["label"].strip(),
                    },
                )

                b_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {b_count} System B entries"
            )
        )

        self.stdout.write(
            self.style.SUCCESS("Import completed successfully.")
        )