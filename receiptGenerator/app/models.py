from django.db import models
from django.db.models import JSONField

class Receipt_Block(models.Model):
    id_receipt = models.CharField(unique=True, max_length = 100)
    #current_hash = models.CharField()
    json_receipt = JSONField()
    timestamp_receipt = models.CharField(max_length = 100)
    timestamp_stored = models.DateTimeField(auto_now_add = True) # to know when the receipt was stored on the database
    #timestamp_updated = models.DateTimeField(auto_now = True)