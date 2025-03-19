from django.db import models

# class TrackSheet(models.Model):
#     SUPPLR = models.CharField(max_length=20)
#     CONDAT = models.DateField()
#     Z_ITEMS = models.BooleanField()
#     LATE = models.IntegerField()
#     ATTN = models.IntegerField()

class Supplier(models.Model):
    SUPPLR = models.CharField(max_length=20, primary_key=True)
    SUPPLR_NAME = models.CharField(max_length=100)
    EMAIL = models.EmailField(max_length = 200)


class Inventory(models.Model):
    PURORD = models.IntegerField()    #PO
    SUPPLR = models.CharField(max_length=20)
    PRODCT = models.CharField(max_length=20)
    ORDQTY = models.IntegerField()
    OUTQTY = models.IntegerField()
    CONDAT = models.DateField()
    NEWCONDAT = models.DateField()
    TYPE = models.CharField(max_length=5)

class Shipments(models.Model):
    purord = models.IntegerField()  # PO
    supplr = models.CharField(max_length=100)
    item = models.CharField(max_length=20)
    ordqty= models.IntegerField()
    outqty = models.IntegerField()
    condat = models.DateField()
    newdate = models.DateField()
    type = models.CharField(max_length=5)
    late = models.IntegerField()
    class Meta:
        db_table = 'shipping_shipment'
        def __str__(self):
            return self.item


