from datetime import date
from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from reconciler.models import Location, SystemARecord, SystemBEntry
from reconciler.services.comparator import find_discrepancies


class ComparatorTests(TestCase):

    def setUp(self):
        self.location = Location.objects.create(
            location_id="LOC-TEST",
            org_id="ORG-TEST",
            location_name="Test Location",
        )

    def create_a(self, record_id="REC-1001", total="100.00"):
        return SystemARecord.objects.create(
            record_id=record_id,
            location=self.location,
            event_date=date(2026, 1, 1),
            category_code="CAT",
            actor_id="ACTOR-1",
            base_value=Decimal("100.00"),
            adjustment=Decimal("0.00"),
            total_value=Decimal(total),
            state="ACTIVE",
        )

    def create_b(self, entry_id, record_ref, value="100.00"):
        return SystemBEntry.objects.create(
            entry_id=entry_id,
            record_ref=record_ref,
            location=self.location,
            recorded_on=date(2026, 1, 1),
            value=Decimal(value),
            label="TEST",
        )

    def test_missing_in_system_b(self):
        self.create_a()
        results = find_discrepancies()
        reasons = [item["reason"] for item in results]
        self.assertIn("MISSING_IN_SYSTEM_B", reasons)

    def test_orphan_in_system_b(self):
        self.create_b("ENT-1", "REC-9999")
        results = find_discrepancies()
        reasons = [item["reason"] for item in results]
        self.assertIn("ORPHAN_IN_SYSTEM_B", reasons)

    def test_duplicate_in_system_b(self):
        self.create_a()
        self.create_b("ENT-1", "REC-1001")
        self.create_b("ENT-2", "REC-1001")

        results = find_discrepancies()
        reasons = [item["reason"] for item in results]
        self.assertIn("DUPLICATE_IN_SYSTEM_B", reasons)

    def test_value_mismatch(self):
        self.create_a(total="100.00")
        self.create_b("ENT-1", "REC-1001", "150.00")

        results = find_discrepancies()
        reasons = [item["reason"] for item in results]
        self.assertIn("VALUE_MISMATCH", reasons)

    def test_tenant_isolation(self):
        other_location = Location.objects.create(
            location_id="LOC-OTHER",
            org_id="ORG-OTHER",
            location_name="Other Location",
        )

        SystemARecord.objects.create(
            record_id="REC-OTHER",
            location=other_location,
            event_date=date(2026, 1, 1),
            category_code="CAT",
            actor_id="ACTOR-2",
            base_value=Decimal("200.00"),
            adjustment=Decimal("0.00"),
            total_value=Decimal("200.00"),
            state="ACTIVE",
        )

        results = find_discrepancies(org_id="ORG-TEST")
        records = [item["record"] for item in results]

        self.assertNotIn("REC-OTHER", records)


    def test_api_requires_org_id(self):
        client = APIClient()

        response = client.get("/api/discrepancies/")

        self.assertEqual(response.status_code, 400)

    def test_api_tenant_isolation(self):
        other_location = Location.objects.create(
            location_id="LOC-OTHER",
            org_id="ORG-OTHER",
            location_name="Other Location",
        )

        SystemARecord.objects.create(
            record_id="REC-OTHER",
            location=other_location,
            event_date=date(2026, 1, 1),
            category_code="CAT",
            actor_id="ACTOR-2",
            base_value=Decimal("200.00"),
            adjustment=Decimal("0.00"),
            total_value=Decimal("200.00"),
            state="ACTIVE",
        )

        client = APIClient()
        response = client.get(
            "/api/discrepancies/?org_id=ORG-TEST"
        )

        self.assertEqual(response.status_code, 200)

        records = [
            item["record"]
            for item in response.data["results"]
        ]

        self.assertNotIn("REC-OTHER", records)