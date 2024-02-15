from django.db import models

class UserProfile(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    job = models.CharField(max_length=100)

    def __str__(self):
        return self.name

