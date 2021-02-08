from django.db import models
from main.models import Stock


class QuarterlyRule40(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateField()
    rule_40 = models.FloatField()
    ebita_ratio = models.FloatField()
    annual_growth = models.FloatField()