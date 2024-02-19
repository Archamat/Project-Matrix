from django.db import models

class UserProfile(models.Model):
    
    CATEGORY_CHOICES = (
        ('0','AI'),
        ('1','WEB'),   
    )
    
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    job = models.CharField(max_length=100)
    category = models.CharField(max_length=200, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.name

