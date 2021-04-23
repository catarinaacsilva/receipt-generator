from django.db import models
from django.db.models import JSONField
from cassandra.cqlengine import columns
from django_cassandra_engine.models import DjangoCassandraModel

'''
class Receipt_Block(models.Model):
    id_receipt = models.CharField(unique=True, max_length = 100)
    #current_hash = models.CharField()
    json_receipt = JSONField()
    timestamp_receipt = models.CharField(max_length = 100)
    timestamp_stored = models.DateTimeField(auto_now_add = True) # to know when the receipt was stored on the database
    #timestamp_updated = models.DateTimeField(auto_now = True)


class Chain(models.Model):
    id_chain = models.AutoField(primary_key=True)
    json_block = JSONField()
    json_receipt = JSONField()
    timestamp = models.DateTimeField(auto_now_add = True)
'''

class Receipt(DjangoCassandraModel):
    email = columns.CharField(unique= False, max_length=100) # email de quem assinou o recibo
    id_receipt = columns.CharField(primary_key=True, max_length=100)
    timestamp = columns.DateTimeField(auto_now_add = True)
    json_receipt = JSONField()