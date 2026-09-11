from collections import defaultdict
import re

from reconciler.models import SystemARecord, SystemBEntry


def normalize_ref(value):
    """Normalize dirty record references into a common format."""
    if not value:
        return ""

    cleaned = re.sub(r"[^a-zA-Z0-9]", "", value).lower()

    if cleaned.isdigit():
        return f"rec{cleaned}"

    return cleaned

def find_discrepancies(org_id=None):
    results = []

    system_a = SystemARecord.objects.select_related("location")
    system_b = SystemBEntry.objects.select_related("location")

    if org_id:
        system_a = system_a.filter(location__org_id=org_id)
        system_b = system_b.filter(location__org_id=org_id)

    b_map = defaultdict(list)

    for b in system_b:
        key = normalize_ref(b.record_ref)

        if key:
            b_map[key].append(b)

    matched_keys = set()

   
    for a in system_a:
        key = normalize_ref(a.record_id)
        entries = b_map.get(key, [])

        if not entries:
            results.append({
                "reason": "MISSING_IN_SYSTEM_B",
                "record": a.record_id,
                "location": a.location.location_id,
                "org": a.location.org_id,
                "system_a": str(a.total_value),
                "system_b": None,
            })
            continue

        if len(entries) > 1:
            results.append({
                "reason": "DUPLICATE_IN_SYSTEM_B",
                "record": a.record_id,
                "location": a.location.location_id,
                "org": a.location.org_id,
                "system_a": str(a.total_value),
                "system_b": ", ".join(
                    str(entry.value) for entry in entries
                ),
            })
            matched_keys.add(key)
            continue

        b = entries[0]
        matched_keys.add(key)

        if a.total_value != b.value:
            results.append({
                "reason": "VALUE_MISMATCH",
                "record": a.record_id,
                "location": a.location.location_id,
                "org": a.location.org_id,
                "system_a": str(a.total_value),
                "system_b": str(b.value),
            })

    for key, entries in b_map.items():
        if key not in matched_keys:
            for b in entries:
                results.append({
                    "reason": "ORPHAN_IN_SYSTEM_B",
                    "record": b.record_ref,
                    "location": b.location.location_id,
                    "org": b.location.org_id,
                    "system_a": None,
                    "system_b": str(b.value),
                })

    return results