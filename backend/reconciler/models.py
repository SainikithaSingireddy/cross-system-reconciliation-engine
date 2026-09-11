from django.db import models


class Location(models.Model):
    location_id = models.CharField(max_length=50, unique=True)
    org_id = models.CharField(max_length=50)
    location_name = models.CharField(max_length=255)

    def __str__(self):
        return self.location_id


class SystemARecord(models.Model):
    record_id = models.CharField(max_length=50, unique=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    event_date = models.DateField(null=True, blank=True)
    category_code = models.CharField(max_length=50, blank=True)
    actor_id = models.CharField(max_length=100, blank=True)
    base_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    adjustment = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    total_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    state = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.record_id


class SystemBEntry(models.Model):
    entry_id = models.CharField(max_length=50, unique=True)
    record_ref = models.CharField(max_length=100)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    recorded_on = models.DateField(null=True, blank=True)
    value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    label = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.entry_id