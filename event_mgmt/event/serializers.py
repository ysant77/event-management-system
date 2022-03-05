from .models import Event, Ticket, Category, Image
from django.contrib.auth.models import User
from rest_flex_fields import FlexFieldsModelSerializer
from versatileimagefield.serializers import VersatileImageFieldSerializer


class CategorySerializer(FlexFieldsModelSerializer):
    """
    Serializer class for category model
    """
    class Meta:
        model = Category
        fields = ['pk', 'name']
        expandable_fields = {
          'events': ('event.EventSerializer', {'many': True})
        }

class EventSerializer(FlexFieldsModelSerializer):
    """
    Serializer class for events model
    """
    class Meta:
        model = Event
        fields = ['pk', 'name', 'description', 'expiration', 'seats', 'created', 'updated']
        expandable_fields = {
            'tickets': ('event.TicketSerializer', {'many':True}),
            'category': ('event.CategorySerializer', {'many': True}),
            'image': ('event.ImageSerializer', {'many': True}),
        }

class TicketSerializer(FlexFieldsModelSerializer):
    """
    Serializer class for tickets model
    """
    class Meta:
        model  = Ticket
        fields = ['pk', 'created', 'updated']
        expandable_fields = {
            'event': 'event.EventSerializer',
            'user': 'event.UserSerializer'
        }

class UserSerializer(FlexFieldsModelSerializer):
    """
    Serializer class for user model (built in user class)
    """
    class Meta:
        model = User
        fields = ['id', 'username']

class ImageSerializer(FlexFieldsModelSerializer):
    """
    Serializer class for image model
    """
    image = VersatileImageFieldSerializer(
        sizes='event_headshot'
    )

    class Meta:
        model = Image
        fields = ['pk', 'name', 'image']