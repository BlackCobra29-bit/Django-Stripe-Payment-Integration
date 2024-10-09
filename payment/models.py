from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class tutorials(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    image = models.URLField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title
    
class Purchaser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchasers')
    purchased_courses = models.ManyToManyField(tutorials, related_name='purchasers', blank=True)
    date_created = models.DateTimeField(auto_now_add=True)  # Automatically set to now when the object is created

    def __str__(self):
        return self.user.username