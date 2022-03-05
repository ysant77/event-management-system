import datetime
from .serializers import EventSerializer, ImageSerializer, TicketSerializer
from .models import Event, Image, Ticket
from rest_framework.viewsets import ModelViewSet
from rest_flex_fields.views import FlexFieldsMixin, FlexFieldsModelViewSet
from rest_flex_fields import is_expanded
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.decorators import api_view, action
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework import status
from rest_framework.response import Response
from threading import Lock, Thread
from rest_framework.permissions import IsAuthenticated, IsAdminUser


class EventViewSet(FlexFieldsMixin, ModelViewSet):
    """
    View set for event related operations. Can only be accessed by authenticated users.
    """

    serializer_class = EventSerializer
    permit_list_expands = ['category', 'tickets']   #will expand as and when needed (if specified)
    filterset_fields = ('category',)    #used to filter the events
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        GET method to fetch all the events and conditionally expand the nested objects in it (category or tickets)
        Input:
            None (nothing except self)
        Output:
            query set which represents the entire event set
        """
        queryset = Event.objects.all()

        if is_expanded(self.request, 'category'):
            queryset = queryset.prefetch_related('category')
            

        if is_expanded(self.request, 'tickets'):
            queryset = queryset.prefetch_related('tickets')

        return queryset


    def create(self, request):
        """
        POST Method to create events. Only superuser/admin can access them.
        Input:
            request => incoming HTTP Request
        Output:
            HTTP response with corresponding status code
        """
        #check to ensure only admin is able to create events
        if request.user.is_superuser == False or request.user.is_staff == False:
            return Response({"status":"error", "data":"You don't have permission to create event"}, status=status.HTTP_401_UNAUTHORIZED)
        
        #if event with this name already exists then return error
        if Event.objects.filter(name=request.data["name"]).exists():
            return Response({"status":"error","data":"Event already exists"},status=status.HTTP_400_BAD_REQUEST)

        serializer = EventSerializer(data=request.data)

        #performs serializer validations
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)

        else:
            return Response({"status": "error", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    
    def update(self, request, pk):
        """
        PUT Method to update existing events. Only superuser/admin can access them.
        Input:
            request => incoming HTTP Request
            pk => primary key of event
        Output:
            HTTP response with corresponding status code
        """

        #check to ensure only admin is able to create events
        if request.user.is_superuser == False or request.user.is_staff == False:
            return Response({"status":"error", "data":"You don't have permission to create event"}, status=status.HTTP_401_UNAUTHORIZED)

        #check if such an event actually exists
        if Event.objects.filter(id=pk).exists():

            event = Event.objects.filter(id=pk).first()
            event.description = request.data['description']
            event.expiration = request.data['expiration']
            #update the number of seats only if incoming object has non zero seats
            if int(request.data["seats"]) > 0:
                event.seats = int(request.data["seats"])

            event.save()
            return  Response({"status":"success","data":"Event successfully updated"},status=status.HTTP_200_OK)
        return Response({"status": "error", "data": "event does not exists!"}, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['GET'])
def register_event(request, pk):
    """
    GET method to register the event specified by pk for current user
    Input:
        request => Incoming HTTP request
        pk => primary key of the event
    Output:
        HTTP response with appropriate status code
    """
    #If user is not authenticated then return error
    if request.user.is_authenticated == False:
        return Response({"status":"error", "data":"Please login"}, status=status.HTTP_401_UNAUTHORIZED)

    event = Event.objects.filter(pk=pk).first()

    #check if event with the given pk exists
    if event is None:
        return Response({"status":"error","data":"Event does not exists"},status=status.HTTP_400_BAD_REQUEST)
    
    expiration_date = event.expiration

    #if event expiration date is today or has already gone
    if expiration_date <= datetime.datetime.now().date():
        return Response({"status":"error", "data":"Event already over or ongoing. Cannot register now"}, status=status.HTTP_400_BAD_REQUEST)

    #if event has no seats left
    if event.seats == 0:
            return Response({"status":"error", "data":"Event registration full"}, status=status.HTTP_400_BAD_REQUEST)
    
    #if user has already registered for the event
    if Ticket.objects.filter(user=request.user, event=event).exists():
        return Response({"status":"error", "data":"Event already regsitered"}, status=status.HTTP_400_BAD_REQUEST)
    
    #lock to atomically update event
    lock = Lock()
    lock.acquire()
    event.seats -= 1
    event.save()
    lock.release()
    
    #register the current user for event and generate a ticket
    ticket = Ticket.objects.create(user=request.user, event=event)

    if ticket is None:
        return Response({"status": "error", "data": "some error occured"}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response({"status": "success", "data": 
        {"pk":ticket.pk, "event name":event.name, "event description":event.description}}, status=status.HTTP_200_OK)


class TicketViewSet(ModelViewSet):
    """
    View set for ticket (ticket represents a registration of a user for a particular event)
    """
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        GET method to return all the tickets for current user.
        Input:
            None (nothing except self)
        Output:
            query set which represents all the tickets for current user
        """

        tickets = Ticket.objects.filter(user=self.request.user)
        if tickets is not None:
            return tickets
        return Response({"status":"error", "data":"No tickets for current user"})

class ImageViewSet(FlexFieldsModelViewSet):
    """
    View set to represent the images associated with events
    """
    serializer_class = ImageSerializer
    queryset = Image.objects.all()
    permission_classes = [IsAuthenticated]
    
