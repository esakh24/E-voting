from django.db import models

# Create your models here.
class adminKeys(models.Model):
    x = models.CharField(default="", max_length=3000) # private key
    p = models.CharField(default="", max_length=3000) # prime cyclic Group
    Y = models.CharField(default="", max_length=3000) # h = g^x % p
    g = models.CharField(default="", max_length=3000) # generator
    bits = models.IntegerField(default=512)
    def __str__(self):
        return str((self.p, self.g, self.bits))