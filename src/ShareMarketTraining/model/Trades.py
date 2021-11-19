from django.db import models
import uuid

class Trade(models.Model):
        STATUSES = (
             ('H', 'HOLDING'),
             ('S', 'SOLD'),
        )
        uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        purchasedAt = models.DecimalField(decimal_places=2)
        numOfShares = models.IntegerField()
        stocksymbol = models.CharField()
        status = models.CharField(max_length=1, choices=STATUSES)


