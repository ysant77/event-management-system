from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from versatileimagefield.fields import VersatileImageField, PPOIField

class Category(models.Model):
    """
    Category model used to specify event by category. Used as a filter on events
    """
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Event(models.Model):
    """
    Event model represents an event. 
    Attributes:
    name (name of event, unique)
    description (event description)
    created (created date)
    updated (updated date)
    expiration (specifies the date till event registration is open)
    seats (maximum number of available seats)
    image (a many to many field having link to image table which store event related images)
    category (another many to many field capturing the event category)
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    expiration = models.DateField(default=datetime.now, editable=True)
    seats = models.IntegerField(default=10)
    image = models.ManyToManyField('event.Image', related_name='events')
    category = models.ManyToManyField(Category, related_name='events')

    class Meta:
        
        #ordering -created will by default show recently created events first
        ordering = ['-created']
    
    def __str__(self):
        return self.name


    

class Ticket(models.Model):
    """
    Ticket represents a booking done by user for an event.
    Attributes:
    event (a foreign key which points to event primary key)
    user (a foreign key which points to event primary key)
    created (created date)
    updated (updated date)
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets', related_query_name='ticket')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets', related_query_name='ticket')
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

class Image(models.Model):
    """
    Image object which represents image stored on server side.
    Attributes:
    name (image name)
    image (image field  of type versatileimage field that stores image's primary point of interest [PPOI])
    """
    name = models.CharField(max_length=255)
    image = VersatileImageField(
        'Image',
        upload_to='images/',
        ppoi_field='image_ppoi'
    )
    image_ppoi = PPOIField()

    def __str__(self):
        return self.name