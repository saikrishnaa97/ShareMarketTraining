from django.db import models
import uuid

class User(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    email = models.EmailField()
    availableBalance = models.DecimalField(decimal_places=2)

