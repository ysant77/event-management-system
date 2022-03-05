from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from versatileimagefield.fields import VersatileImageField, PPOIField

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    expiration = models.DateField(default=datetime.now, editable=True)
    seats = models.IntegerField(default=10)
    image = models.ManyToManyField('event.Image', related_name='events')
    category = models.ManyToManyField(Category, related_name='events')

    class Meta:
        ordering = ['-created']
    
    def __str__(self):
        return self.name


    

class Ticket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets', related_query_name='ticket')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets', related_query_name='ticket')
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

class Image(models.Model):
    name = models.CharField(max_length=255)
    image = VersatileImageField(
        'Image',
        upload_to='images/',
        ppoi_field='image_ppoi'
    )
    image_ppoi = PPOIField()

    def __str__(self):
        return self.name