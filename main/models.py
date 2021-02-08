from django.db import models


class Stock(models.Model):
    symbol = models.CharField(max_length=200)