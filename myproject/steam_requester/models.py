from django.db import models

class User(models.Model):
    id = models.IntegerField(primary_key=True)
    amount_of_cases = models.IntegerField(default=0)
    is_traded = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)