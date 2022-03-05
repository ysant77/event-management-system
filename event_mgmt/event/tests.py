import json


from django.contrib.auth.models import User
from django.urls import reverse

from .models import Event, Ticket

from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from .views import EventViewSet, TicketViewSet, register_event

class EventViewSetAPITestCase(APITestCase):
    url = reverse("auth_logout")
    def setUp(self):
        self.username = "tester"
        self.password = "tester123@"
        self.first_name = "test"
        self.last_name = "test"
        self.email = "test@test.com"
        self.user = User.objects.create_user(self.username, self.email, self.password)
        self.event = Event.objects.create(name="testevent", seats=10, expiration="2022-03-20")
        

        self.factory = APIRequestFactory()
        self.admin_pass = "yatharth123@"
        self.adminuser = User.objects.create_superuser('yatharth','yatharth@gmail.com',self.admin_pass)
        
    
    def test_authenticated_users_can_view_events(self):
        """
        Test to verify that authenticated user can see all events
        """
        response = self.client.post(reverse("token_obtain_pair"), {"username": self.username, "password": self.password})
        contents = json.loads(response.content.decode())
        request = self.factory.get("")
        force_authenticate(request, user=self.user, token=contents["access"])

        #make a request to the event view set
        event_list = EventViewSet.as_view({'get':'list'})
        response = event_list(request)
        self.assertEqual(200, response.status_code)

    def test_authenticated_users_can_view_event_with_pk(self):
        """
        Test to verify that authenticated user can see a particular event specified by its pk
        """
        response = self.client.post(reverse("token_obtain_pair"), {"username": self.username, "password": self.password})
        contents = json.loads(response.content.decode())
        request = self.factory.get("")
        force_authenticate(request, user=self.user, token=contents["access"])
        
        event_detail = EventViewSet.as_view({'get':'retrieve'})
        response = event_detail(request, pk=self.event.pk)
        self.assertEqual(200, response.status_code)
    
    def test_unauthenticated_user_cannot_access_events(self):
        """
        Test to verify that unauthenticated user cannot access events
        """
        request = self.factory.get("")
        event_list = EventViewSet.as_view({'get':'list'})
        response = event_list(request)
        self.assertEqual(401, response.status_code)
    
    def test_authenticated_user_cannot_create_event(self):
        """
        Test to verify that authenticated user cannot create event (only admin can)
        """
        response = self.client.post(reverse("token_obtain_pair"), {"username": self.username, "password": self.password})
        contents = json.loads(response.content.decode())
        data = {
            "name":"event",
            "description":"eventdesc",
            "seats":10,
            "expiration":"2022-03-10"
        }
        request = self.factory.post("", data=data)
        force_authenticate(request, user=self.user, token=contents["access"])
        event_create = EventViewSet.as_view({'post':'create'})
        response = event_create(request)
        self.assertEqual(401, response.status_code)

    def test_authenticated_user_cannot_update_event(self):
        """
        Test to verify that authenticated user cannot update event (only admin can)
        """
        response = self.client.post(reverse("token_obtain_pair"), {"username": self.username, "password": self.password})
        contents = json.loads(response.content.decode())
        data = {
            "name":"event",
            "description":"eventdesc",
            "seats":10,
            "expiration":"2022-03-10"
        }
        request = self.factory.put("", data=data)
        force_authenticate(request, user=self.user, token=contents["access"])
        event_update = EventViewSet.as_view({'put':'update'})
        response = event_update(request, pk=self.event.pk)
        self.assertEqual(401, response.status_code)
    
    def test_admin_can_create_event(self):
        """
        Test to verify that admin can create event
        """
        response = self.client.post(reverse("token_obtain_pair"), {"username": "yatharth", "password": self.admin_pass})
        contents = json.loads(response.content.decode())
        data = {
            "name":"event",
            "description":"eventdesc",
            "seats":10,
            "expiration":"2022-03-10"
        }
        
        request = self.factory.post("", data=data,format="json")

        
        force_authenticate(request, user=self.adminuser, token=contents["access"])
        event_create = EventViewSet.as_view({'post':'create'})
        response = event_create(request)
        
        
        response_contents = json.loads(response.rendered_content.decode())
        
        self.assertEqual(201, response.status_code)
        self.assertDictContainsSubset(data, response_contents["data"])
    def test_admin_can_update_event(self):
        """
        Test to verify that admin can update event
        """
        response = self.client.post(reverse("token_obtain_pair"), {"username": "yatharth", "password": self.admin_pass})
        contents = json.loads(response.content.decode())
        data = {
            "name":"event",
            "description":"eventdesc",
            "seats":10,
            "expiration":"2022-03-10"
        }
        
        request = self.factory.put("", data=data,format="json")

        
        force_authenticate(request, user=self.adminuser, token=contents["access"])
        event_create = EventViewSet.as_view({'put':'update'})
        response = event_create(request, pk=self.event.pk)
        
        
        response_contents = json.loads(response.rendered_content.decode())
        self.assertEqual(200, response.status_code)
    
class TicketModelViewSetAPITestCase(APITestCase):
    
    def setUp(self):
        self.username = "tester"
        self.password = "tester123@"
        self.first_name = "test"
        self.last_name = "test"
        self.email = "test@test.com"
        self.user = User.objects.create_user(self.username, self.email, self.password)
        self.event = Event.objects.create(name="testevent", seats=10, expiration="2022-03-20")
        self.url = reverse( "event_register" , kwargs={"pk":self.user.pk})

        self.factory = APIRequestFactory()
        self.admin_pass = "yatharth123@"
        self.adminuser = User.objects.create_superuser('yatharth','yatharth@gmail.com',self.admin_pass)
    
    def test_unauthenticated_user_cannot_register_for_event(self):
        """
        Test to verify that unauthenticated user cannot register for event
        """
        request = self.factory.get(self.url)
        response = register_event(request, pk=10)
        self.assertEqual(401, response.status_code)
    
    def test_authenticated_user_cannot_register_for_non_existing_event(self):
        """
        Test to verify that authenticated user cannot register for event which does not exist
        """
        response = self.client.post(reverse("token_obtain_pair"), {"username": self.username, "password": self.password})
        contents = json.loads(response.content.decode())
        request = self.factory.get(self.url)
        force_authenticate(request, user=self.adminuser, token=contents["access"])
        
        response = register_event(request, pk=100)
        
        self.assertEqual(400, response.status_code)
    
    def test_authenticated_user_cannot_register_for_events_happening_today_or_in_past(self):
        """
        Test to verify that authenticated user cannot register for event that happens today or has already happened in past
        """
        response = self.client.post(reverse("token_obtain_pair"), {"username": self.username, "password": self.password})
        contents = json.loads(response.content.decode())
        request = self.factory.get(self.url)
        force_authenticate(request, user=self.adminuser, token=contents["access"])
        event = Event.objects.create(name="testevent1", seats=10, expiration="2022-03-04")
        response = register_event(request, pk=event.pk)
        self.assertEqual(400, response.status_code)

    def test_authenticated_user_cannot_register_for_events_having_zero_seats(self):
        """
        Test to verify that authenticated user cannot register for an event having 0 seats left
        """
        response = self.client.post(reverse("token_obtain_pair"), {"username": self.username, "password": self.password})
        contents = json.loads(response.content.decode())
        request = self.factory.get(self.url)
        force_authenticate(request, user=self.adminuser, token=contents["access"])
        event = Event.objects.create(name="testevent2", seats=0, expiration="2022-03-14")
        response = register_event(request, pk=event.pk)
        self.assertEqual(400, response.status_code)
    
    def test_authenticated_users_cannot_register_for_already_registered_event(self):
        """
        Test to verify that authenticated user cannot register for already registered event
        """
        response = self.client.post(reverse("token_obtain_pair"), {"username": self.username, "password": self.password})
        contents = json.loads(response.content.decode())
        request = self.factory.get(self.url)
        force_authenticate(request, user=self.adminuser, token=contents["access"])
        event = Event.objects.create(name="testevent3", seats=10, expiration="2022-03-14")
        ticket = Ticket.objects.create(user=self.user, event=event)
        response = register_event(request, pk=self.user.pk)
        self.assertEqual(400, response.status_code)
    
    def test_authenticated_users_can_register_for_new_event(self):
        """
        Test to verify that authenticated user can register for a new event
        """
        response = self.client.post(reverse("token_obtain_pair"), {"username": self.username, "password": self.password})
        contents = json.loads(response.content.decode())
        request = self.factory.get(self.url)
        force_authenticate(request, user=self.adminuser, token=contents["access"])
        
        response = register_event(request, pk=self.event.pk)
        self.assertEqual(200, response.status_code)
        event = Event.objects.filter(pk=self.event.pk).first()
        self.assertEqual(9, event.seats)
    
    def test_unauthenticated_users_cannot_retrieve_tickets(self):
        """
        Test to verify that unauthenticated user cannot retrieve tickets
        """
        request = self.factory.get("")
        ticket_list = TicketViewSet.as_view({'get':'list'})
        response = ticket_list(request)
        self.assertEqual(401, response.status_code)

    def test_authenticated_users_can_only_retrieve_their_own_tickets(self):
        """
        Test to verify that authenticated users can view their own tickets
        """
        response = self.client.post(reverse("token_obtain_pair"), {"username": self.username, "password": self.password})
        contents = json.loads(response.content.decode())
        request = self.factory.get("")
        force_authenticate(request, user=self.adminuser, token=contents["access"])
        response = register_event(request, pk=self.event.pk)
        self.assertEqual(200, response.status_code)

        ticket_list = TicketViewSet.as_view({'get':'list'})
        response = ticket_list(request)
        response_contents = json.loads(response.rendered_content.decode())
       
        self.assertEqual(200, response.status_code)