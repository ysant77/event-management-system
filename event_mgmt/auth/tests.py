import json

from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from .views import LogoutView, ChangePasswordView, UpdateProfileView

class RegisterViewAPITestCase(APITestCase):
    url = reverse("auth_register")

    def test_password_confirmpassword_different(self):
        """
        Test to verify that a register user fails if password and confirm are different
        """

        user_data = {
            "username":"testuser",
            "email":"testuser@test.com",
            "first_name":"test1",
            "last_name":"user",
            "password":"test123@",
            "confirmpassword":"ttttt"
        }
        #make a post request with the payload
        response = self.client.post(self.url, user_data)
        #decode the binary response
        response_content = json.loads(response.content.decode())
        
        self.assertEqual(400, response.status_code)
        self.assertEqual("Password fields didn't match.", response_content["password"][0])
    
    def test_user_registration(self):
        """
        Test to verify that with correct payload a new user is created successfully
        """
        user_data = {
            "username":"testuser",
            "email":"testuser@test.com",
            "first_name":"test1",
            "last_name":"user",
            "password":"test123@",
            "confirmpassword":"test123@"
        }
        response = self.client.post(self.url, user_data)
        response_content = json.loads(response.content.decode())
        
        self.assertEqual(201, response.status_code)
        #response data won't be having password and hence response is a subset of request payload
        self.assertDictContainsSubset(response_content, user_data)
    

    def test_unique_username_validation(self):
        """
        Test to verify that unique validation of username is correctly implemented
        """
        user_data_1 = {
            "username":"testuser",
            "email":"testuser@test.com",
            "first_name":"test1",
            "last_name":"user",
            "password":"test123@",
            "confirmpassword":"test123@"
        }
        response = self.client.post(self.url, user_data_1)
        response_content = json.loads(response.content.decode())
        
        self.assertEqual(201, response.status_code)
        self.assertDictContainsSubset(response_content, user_data_1)
        #try creating user with same username
        user_data_2 = {
            "username":"testuser",
            "email":"testuser1@test.com",
            "first_name":"test1",
            "last_name":"user",
            "password":"test123@",
            "confirmpassword":"test123@"
        }
        response = self.client.post(self.url, user_data_2)
        response_content = json.loads(response.content.decode())
       
        self.assertEqual(400, response.status_code)
        self.assertEqual("A user with that username already exists.", response_content['username'][0])
        
    def test_unique_email_validation(self):
        """
        Test to verify that unique validation of email is correctly implemented
        """
        user_data_1 = {
            "username":"testuser",
            "email":"testuser@test.com",
            "first_name":"test1",
            "last_name":"user",
            "password":"test123@",
            "confirmpassword":"test123@"
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
            "confirmpassword":"test123@"
        }
        #another request payload with same email id as that of earlier
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
        """
        Test to verify that login fails if no password is given
        """
        response = self.client.post(self.url, {"username": self.username})
        self.assertEqual(400, response.status_code)

    def test_authentication_with_wrong_password(self):
        """
        Test to verify that login fails if password is incorrect
        """
        response = self.client.post(self.url, {"username": self.username, "password": "I_know"})
        self.assertEqual(401, response.status_code)

    def test_authentication_with_valid_data(self):
        """
        Test to verify that user is logged in with correct credentials and a pair of access/refresh tokens is returned
        """
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
        """
        Test to verify that logout fails if invalid refresh token is passed
        """
        data = {
            "refresh_token":"sjsjwhwuwhbbsbhququshxx"
        }
        response = self.client.post(reverse("token_obtain_pair"), {"username": self.username, "password": self.password})
        response = self.client.post(self.url, data)
        response_contents = json.loads(response.content.decode())
        self.assertEqual(401, response.status_code)
        self.assertEqual("Authentication credentials were not provided.", response_contents["detail"])

    def test_logout_with_valid_token(self):
        """
        Test to verify that logout succeeds if valid refresh token in passed
        """
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
    
    def test_password_confirmpassword_different(self):
        """
        Test to verify that password change would fail if password and confirm passwords are different
        """


        user_data = {
            "password":"test123@",
            "confirmpassword":"ttttt",
            "old_password":"tester123@"
        }
        response = self.client.post(reverse("token_obtain_pair"), {"username": self.username, "password": self.password})
        contents = json.loads(response.content.decode())
       
        #get a put request from api request factory and forcefully authenticate the user
        request = self.factory.put(self.url, data=user_data)
        force_authenticate(request, user=self.user, token=contents["access"])

        
        view = ChangePasswordView.as_view()
        #send request to change password view now
        response = view(request, pk=self.user.pk)
        
        self.assertEqual(400, response.status_code)

    def test_password_oldpassword_different(self):
        """
        Test to verify that change password fails if old password is not correct
        """


        user_data = {
            "password":"test123@",
            "confirmpassword":"test123@",
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
        Test to verify that change passwords would succeed if all validations succeed
        """


        user_data = {
            "password":"test1234@",
            "confirmpassword":"test1234@",
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
        Test to verify that update profile fails if new email already exists in database
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
        Test to verify that update profile fails if new username already exists in database
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
        Test to verify that update profile succeeds if all validations succeed
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
    
    