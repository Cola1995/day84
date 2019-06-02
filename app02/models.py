from django.db import models
# Create your models here.


class Order(models.Model):
    title = models.CharField(max_length=32)

    def __str__(self):
        return self.title


class Food(models.Model):
    title = models.CharField(max_length=32)

    def __str__(self):
        return self.title
