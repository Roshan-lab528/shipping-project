from django.db import models

class ShippingRate(models.Model):
    date = models.DateField(null=True, blank=True)

    shipping_line = models.CharField(max_length=100, blank=True, null=True)
    origin_port_name = models.CharField(max_length=150, blank=True, null=True)
    destination_port_name = models.CharField(max_length=150, blank=True, null=True)

    container_size = models.CharField(max_length=50, blank=True, null=True)
    kgs = models.IntegerField(null=True, blank=True)

    valid_from_etd = models.CharField(max_length=100, blank=True, null=True)
    valid_to_eta = models.CharField(max_length=100, blank=True, null=True)

    # ✅ ALL COST FIELDS (STRING)
    ocean_freight = models.CharField(max_length=100, blank=True, null=True)
    freight_surcharge = models.CharField(max_length=100, blank=True, null=True)
    export_surcharge = models.CharField(max_length=100, blank=True, null=True)
    import_surcharge = models.CharField(max_length=100, blank=True, null=True)

    total_cost_usd = models.FloatField(null=True, blank=True)

    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.shipping_line} | {self.origin_port_name} → {self.destination_port_name}"
