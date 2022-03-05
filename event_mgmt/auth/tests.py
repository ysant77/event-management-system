import json

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.urls import reverse

from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from .views import LogoutView, ChangePasswordView, UpdateProfileView

class RegisterViewAPITestCase(APITestCase):
    url = reverse("auth_register")

    def test_password_password2_different(self):
        """
        Test to verify that a post call with invalid passwords
        """

        user_data = {
            "username":"testuser",
            "email":"testuser@test.com",
            "first_name":"test1",
            "last_name":"user",
            "password":"test123@",
            "password2":"ttttt"
        }
        response = self.client.post(self.url, user_data)
        response_content = json.loads(response.content.decode())
        
        self.assertEqual(400, response.status_code)
        self.assertEqual("Password fields didn't match.", response_content["password"][0])
    
    def test_user_registration(self):
        """
        Test to verify that a post call with valid user data creates user 
        """
        user_data = {
            "username":"testuser",
            "email":"testuser@test.com",
            "first_name":"test1",
            "last_name":"user",
            "password":"test123@",
            "password2":"test123@"
        }
        response = self.client.post(self.url, user_data)
        response_content = json.loads(response.content.decode())
        
        self.assertEqual(201, response.status_code)
        self.assertDictContainsSubset(response_content, user_data)
    

    def test_unique_username_validation(self):
        """
        Test to verify that username is unique
        """
        user_data_1 = {
            "username":"testuser",
            "email":"testuser@test.com",
            "first_name":"test1",
            "last_name":"user",
            "password":"test123@",
            "password2":"test123@"
        }
        response = self.client.post(self.url, user_data_1)
        response_content = json.loads(response.content.decode())
        
        self.assertEqual(201, response.status_code)
        self.assertDictContainsSubset(response_content, user_data_1)
        user_data_2 = {
            "username":"testuser",
            "email":"testuser@test.com",
            "first_name":"test1",
            "last_name":"user",
            "password":"test123@",
            "password2":"test123@"
        }
        response = self.client.post(self.url, user_data_2)
        response_content = json.loads(response.content.decode())
       
        self.assertEqual(400, response.status_code)
        self.assertEqual("A user with that username already exists.", response_content['username'][0])
        
    def test_unique_email_validation(self):
        """
        Test to verify that email is unique
        """
        user_data_1 = {
            "username":"testuser",
            "email":"testuser@test.com",
            "first_name":"test1",
            "last_name":"user",
            "password":"test123@",
            "password2":"test123@"
        }
        response = self.client.post(self.url, user_data_1)
        response_content = json.loads(response.content.decode())
        
        self.assertEqual(201, response.status_code)
        self.assertDictContainsSubset(response_content, user_data_1)
        user_data_2 = {
            "username":"testuser1",
            "email":"testuser@test.com",
            "first_name":"test1",
            "last_name":"user",
            "password":"test123@",
            "password2":"test123@"
        }
        response = self.client.post(self.url, user_data_2)
        response_content = json.loads(response.content.decode())
       
        self.assertEqual(400, response.status_code)
        self.assertEqual("This field must be unique.", response_content['email'][0])
    
class LoginAPIViewTestCase(APITestCase):
    url = reverse("token_obtain_pair")
    def setUp(self):
        self.username = "tester"
        self.password = "tester123@"
        self.first_name = "test"
        self.last_name = "test"
        self.email = "test@test.com"
        self.user = User.objects.create_user(self.username, self.email, self.password)
        
    def test_authentication_without_password(self):
        response = self.client.post(self.url, {"username": self.username})
        self.assertEqual(400, response.status_code)

    def test_authentication_with_wrong_password(self):
        response = self.client.post(self.url, {"username": self.username, "password": "I_know"})
        self.assertEqual(401, response.status_code)

    def test_authentication_with_valid_data(self):
        response = self.client.post(self.url, {"username": self.username, "password": self.password})

        response_content = json.loads(response.content.decode())
        
        self.assertEqual(200, response.status_code)
        self.assertTrue("access" in response_content)
        self.assertTrue("refresh" in response_content)

class LogoutAPIViewTestCase(APITestCase):
    url = reverse("auth_logout")
    def setUp(self):
        self.username = "tester"
        self.password = "tester123@"
        self.first_name = "test"
        self.last_name = "test"
        self.email = "test@test.com"
        self.user = User.objects.create_user(self.username, self.email, self.password)
        self.factory = APIRequestFactory()

    
    def test_logout_with_invalid_token(self):
        data = {
            "refresh_token":"sjsjwhwuwhbbsbhququshxx"
        }
        response = self.client.post(reverse("token_obtain_pair"), {"username": self.username, "password": self.password})
        response = self.client.post(self.url, data)
        response_contents = json.loads(response.content.decode())
        self.assertEqual(401, response.status_code)
        self.assertEqual("Authentication credentials were not provided.", response_contents["detail"])

    def test_logout_with_valid_token(self):
        
        response = self.client.post(reverse("token_obtain_pair"), {"username": self.username, "password": self.password})
        contents = json.loads(response.content.decode())
        data = {
            "refresh_token":contents["refresh"]
        }
        
        request = self.factory.post(self.url, data=data)
        force_authenticate(request, user=self.user, token=contents["access"])
        view = LogoutView.as_view()
        response = view(request)
        
        self.assertEqual(205, response.status_code)


class ChangePasswordViewAPITestCase(APITestCase):
    
    def setUp(self):
        self.username = "tester"
        self.password = "tester123@"
        self.first_name = "test"
        self.last_name = "test"
        self.email = "test@test.com"
        self.user = User.objects.create_user(self.username, self.email, self.password)
        self.url = reverse("auth_change_password", kwargs={"pk":self.user.pk})
        self.factory = APIRequestFactory()
    
    def test_password_password2_different(self):
        """
        Test to verify that a post call with invalid passwords
        """


        user_data = {
            "password":"test123@",
            "password2":"ttttt",
            "old_password":"tester123@"
        }
        response = self.client.post(reverse("token_obtain_pair"), {"username": self.username, "password": self.password})
        contents = json.loads(response.content.decode())
       
        request = self.factory.put(self.url, data=user_data)
        force_authenticate(request, user=self.user, token=contents["access"])

        
        view = ChangePasswordView.as_view()
        response = view(request, pk=self.user.pk)
        
        self.assertEqual(400, response.status_code)

    def test_password_oldpassword_different(self):
        """
        Test to verify that a put call with invalid passwords
        """


        user_data = {
            "password":"test123@",
            "password2":"test123@",
            "old_password":"test123"
        }
        response = self.client.post(reverse("token_obtain_pair"), {"username": self.username, "password": self.password})
        contents = json.loads(response.content.decode())
        
        request = self.factory.put(self.url, data=user_data)
        force_authenticate(request, user=self.user, token=contents["access"])

        
        view = ChangePasswordView.as_view()
        response = view(request, pk=self.user.pk)
        
        self.assertEqual(400, response.status_code)
    def test_change_password(self):
        """
        Test to verify that a put call with valid passwords
        """


        user_data = {
            "password":"test1234@",
            "password2":"test1234@",
            "old_password":"tester123@"
        }
        response = self.client.post(reverse("token_obtain_pair"), {"username": self.username, "password": self.password})
        contents = json.loads(response.content.decode())
       
        request = self.factory.put(self.url, data=user_data)
        force_authenticate(request, user=self.user, token=contents["access"])

        
        view = ChangePasswordView.as_view()
        response = view(request, pk=self.user.pk)
        
        self.assertEqual(200, response.status_code)

class UpdateProfileViewAPITestCase(APITestCase):
    
    def setUp(self):
        self.username = "tester"
        self.password = "tester123@"
        self.first_name = "test"
        self.last_name = "test"
        self.dummyusername = "dummy"
        self.dummyemail = "dummy@dummy.com"
        self.dummypass = "dummy123@"


        self.email = "test@test.com"
        self.user = User.objects.create_user(self.username, self.email, self.password)
        self.dummyuser = User.objects.create_user(self.dummyusername, self.dummyemail, self.dummypass)
        self.url = reverse("auth_change_password", kwargs={"pk":self.user.pk})
        self.factory = APIRequestFactory()
    
    def test_update_profile_with_existing_email(self):
        """
        Test to verify that a post call with invalid passwords
        """


        user_data = {
            "username":"user101",
            "email":self.dummyemail,
            "first_name":"yatharth",
            "last_name":"sant"
        }
        
        response = self.client.post(reverse("token_obtain_pair"), {"username": self.username, "password": self.password})
        contents = json.loads(response.content.decode())
        
        request = self.factory.put(self.url, data=user_data)
        force_authenticate(request, user=self.user, token=contents["access"])

        
        view = UpdateProfileView.as_view()
        response = view(request, pk=self.user.pk)
        
        self.assertEqual(400, response.status_code)

    def test_update_profile_with_existing_username(self):
        """
        Test to verify that a post call with invalid passwords
        """


        user_data = {
            "username":self.dummyuser,
            "email":"another@email.com",
            "first_name":"yatharth",
            "last_name":"sant"
        }
        
        response = self.client.post(reverse("token_obtain_pair"), {"username": self.username, "password": self.password})
        contents = json.loads(response.content.decode())
        
        request = self.factory.put(self.url, data=user_data)
        force_authenticate(request, user=self.user, token=contents["access"])
        
        
        view = UpdateProfileView.as_view()
        response = view(request, pk=self.user.pk)
        
        self.assertEqual(400, response.status_code)

    def test_update_profile_with_existing_username(self):
        """
        Test to verify that a post call with invalid passwords
        """


        user_data = {
            "username":"user404",
            "email":"another@email.com",
            "first_name":"yatharth",
            "last_name":"sant"
        }
        
        response = self.client.post(reverse("token_obtain_pair"), {"username": self.username, "password": self.password})
        contents = json.loads(response.content.decode())
        
        request = self.factory.put(self.url, data=user_data)
        force_authenticate(request, user=self.user, token=contents["access"])
        
        
        view = UpdateProfileView.as_view()
        response = view(request, pk=self.user.pk)
        
        self.assertEqual(200, response.status_code)
    
    