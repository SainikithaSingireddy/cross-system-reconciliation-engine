from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from .models import Location, SystemARecord, SystemBEntry
from .services.comparator import find_discrepancies


class ComparatorTests(TestCase):

    def setUp(self):
        self.location_a = Location.objects.create(
            location_id="LOC-101",
            org_id="ORG-A",
            location_name="Location A",
        )

        self.location_b = Location.objects.create(
            location_id="LOC-201",
            org_id="ORG-B",
            location_name="Location B",
        )

    def test_missing_in_system_b(self):
        SystemARecord.objects.create(
            record_id="REC-1001",
            location=self.location_a,
            total_value=Decimal("100.00"),
        )

        results = find_discrepancies(org_id="ORG-A")

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0]["reason"],
            "MISSING_IN_SYSTEM_B",
        )
        self.assertEqual(
            results[0]["record"],
            "REC-1001",
        )

    def test_orphan_in_system_b(self):
        SystemBEntry.objects.create(
            entry_id="ENT-1001",
            record_ref="REC-9999",
            location=self.location_a,
            value=Decimal("100.00"),
        )

        results = find_discrepancies(org_id="ORG-A")

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0]["reason"],
            "ORPHAN_IN_SYSTEM_B",
        )
        self.assertEqual(
            results[0]["record"],
            "REC-9999",
        )

    def test_duplicate_in_system_b(self):
        SystemARecord.objects.create(
            record_id="REC-1002",
            location=self.location_a,
            total_value=Decimal("100.00"),
        )

        SystemBEntry.objects.create(
            entry_id="ENT-1002-A",
            record_ref="REC-1002",
            location=self.location_a,
            value=Decimal("100.00"),
        )

        SystemBEntry.objects.create(
            entry_id="ENT-1002-B",
            record_ref="REC-1002",
            location=self.location_a,
            value=Decimal("100.00"),
        )

        results = find_discrepancies(org_id="ORG-A")

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0]["reason"],
            "DUPLICATE_IN_SYSTEM_B",
        )

    def test_value_mismatch(self):
        SystemARecord.objects.create(
            record_id="REC-1003",
            location=self.location_a,
            total_value=Decimal("100.00"),
        )

        SystemBEntry.objects.create(
            entry_id="ENT-1003",
            record_ref="REC-1003",
            location=self.location_a,
            value=Decimal("120.00"),
        )

        results = find_discrepancies(org_id="ORG-A")

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0]["reason"],
            "VALUE_MISMATCH",
        )
        self.assertEqual(
            results[0]["system_a"],
            "100.00",
        )
        self.assertEqual(
            results[0]["system_b"],
            "120.00",
        )

    def test_comparator_tenant_isolation(self):
        SystemARecord.objects.create(
            record_id="REC-A",
            location=self.location_a,
            total_value=Decimal("100.00"),
        )

        SystemBEntry.objects.create(
            entry_id="ENT-A",
            record_ref="REC-A",
            location=self.location_a,
            value=Decimal("120.00"),
        )

        SystemARecord.objects.create(
            record_id="REC-B",
            location=self.location_b,
            total_value=Decimal("200.00"),
        )

        SystemBEntry.objects.create(
            entry_id="ENT-B",
            record_ref="REC-B",
            location=self.location_b,
            value=Decimal("220.00"),
        )

        results = find_discrepancies(org_id="ORG-A")

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0]["record"],
            "REC-A",
        )

        self.assertNotIn(
            "REC-B",
            [result["record"] for result in results],
        )

    def test_api_requires_org_id(self):
        client = APIClient()

        response = client.get("/api/discrepancies/")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["error"],
            "org_id is required",
        )

    def test_api_tenant_isolation(self):
        SystemARecord.objects.create(
            record_id="REC-A",
            location=self.location_a,
            total_value=Decimal("100.00"),
        )

        SystemBEntry.objects.create(
            entry_id="ENT-A",
            record_ref="REC-A",
            location=self.location_a,
            value=Decimal("120.00"),
        )

        SystemARecord.objects.create(
            record_id="REC-B",
            location=self.location_b,
            total_value=Decimal("200.00"),
        )

        SystemBEntry.objects.create(
            entry_id="ENT-B",
            record_ref="REC-B",
            location=self.location_b,
            value=Decimal("220.00"),
        )

        client = APIClient()

        response = client.get(
            "/api/discrepancies/?org_id=ORG-A"
        )

        self.assertEqual(response.status_code, 200)

        records = [
            result["record"]
            for result in response.data["results"]
        ]

        self.assertIn("REC-A", records)
        self.assertNotIn("REC-B", records)

    def test_dirty_reference_formats_match(self):
        location = Location.objects.create(
            location_id="LOC-1112",
            org_id="ORG-TEST",
            location_name="Test Location",
        )

        SystemARecord.objects.create(
            record_id="REC-1112",
            location=location,
            total_value=Decimal("100.00"),
        )

        SystemBEntry.objects.create(
            entry_id="ENT-TEST-1112",
            record_ref="1112",
            location=location,
            value=Decimal("100.00"),
        )

        results = find_discrepancies(
            org_id="ORG-TEST"
        )

        self.assertEqual(results, [])

    def test_invalid_system_b_value_is_not_crash(self):
        location = Location.objects.create(
            location_id="LOC-1064",
            org_id="ORG-TEST",
            location_name="Test Location",
        )

        SystemARecord.objects.create(
            record_id="REC-1064",
            location=location,
            total_value=Decimal("183244.16"),
        )

        SystemBEntry.objects.create(
            entry_id="ENT-TEST-1064",
            record_ref="REC-1064",
            location=location,
            value=None,
        )

        results = find_discrepancies(
            org_id="ORG-TEST"
        )

        self.assertEqual(len(results), 1)

        self.assertEqual(
            results[0]["reason"],
            "VALUE_MISMATCH",
        )

        self.assertIsNone(
            results[0]["system_b"],
        )

    def test_duplicate_system_b_entries_are_reported(self):
        location = Location.objects.create(
            location_id="LOC-1042",
            org_id="ORG-TEST",
            location_name="Test Location",
        )

        SystemARecord.objects.create(
            record_id="REC-1042",
            location=location,
            total_value=Decimal("100.00"),
        )

        SystemBEntry.objects.create(
            entry_id="ENT-1",
            record_ref="REC-1042",
            location=location,
            value=Decimal("100.00"),
        )

        SystemBEntry.objects.create(
            entry_id="ENT-2",
            record_ref="REC-1042",
            location=location,
            value=Decimal("100.00"),
        )

        results = find_discrepancies(
            org_id="ORG-TEST"
        )

        self.assertEqual(len(results), 1)

        self.assertEqual(
            results[0]["reason"],
            "DUPLICATE_IN_SYSTEM_B",
        )