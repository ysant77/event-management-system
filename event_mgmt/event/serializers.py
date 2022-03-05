from .models import Event, Ticket, Category, Image
from django.contrib.auth.models import User
from rest_flex_fields import FlexFieldsModelSerializer
from versatileimagefield.serializers import VersatileImageFieldSerializer


class CategorySerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Category
        fields = ['pk', 'name']
        expandable_fields = {
          'events': ('event.EventSerializer', {'many': True})
        }

class EventSerializer(FlexFieldsModelSerializer):

    class Meta:
        model = Event
        fields = ['pk', 'name', 'description', 'expiration', 'seats', 'created', 'updated']
        expandable_fields = {
            'tickets': ('event.TicketSerializer', {'many':True}),
            'category': ('event.CategorySerializer', {'many': True}),
            'image': ('event.ImageSerializer', {'many': True}),
        }

class TicketSerializer(FlexFieldsModelSerializer):

    class Meta:
        model  = Ticket
        fields = ['pk', 'created', 'updated']
        expandable_fields = {
            'event': 'event.EventSerializer',
            'user': 'event.UserSerializer'
        }

class UserSerializer(FlexFieldsModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username']

class ImageSerializer(FlexFieldsModelSerializer):
    image = VersatileImageFieldSerializer(
        sizes='event_headshot'
    )

    class Meta:
        model = Image
        fields = ['pk', 'name', 'image']