from django.db import models
from django.contrib.postgres.fields import JSONField

class Receipt_Block(models.Model):
    id_receipt = models.CharField(unique=True)
    timestamp_stored = models.DateTimeField(auto_now_add = True)
    current_hash = models.CharField()
    json_receipt = JSONField()
    #timestamp_receipt = models.CharField()
    #timestamp_stored = models.DateTimeField(auto_now_add = True) # to know when the receipt was stored on the database
    #timestamp_updated = models.DateTimeField(auto_now = True)

    def managerReceipts(self, id_receipt, timestamp_stored, current_hash, json_receipt):
        self.id_receipt = id_receipt
        self.timestamp_stored = timestamp_stored
        self.current_hash = current_hash
        self.json_receipt = json_receipt