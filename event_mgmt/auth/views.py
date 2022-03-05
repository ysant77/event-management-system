from .serializers import RegisterSerializer, ChangePasswordSerializer, UpdateUserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken


class RegisterView(generics.CreateAPIView):
    """
    View to register new users.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class ChangePasswordView(generics.UpdateAPIView):
    """
    View to change password. Only authenticated user can access this endpoint.
    """
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer


class UpdateProfileView(generics.UpdateAPIView):
    """
    View to update user profile. Only authenticated user can access this endpoint.
    """
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateUserSerializer


class LogoutView(APIView):
    """
    View to logout the user. Only authenticated user can access this endpoint.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        This method will accept the refresh token generated while user login and black list it.
        Input:
            request => object that should have refresh_token
        Output:
            HTTP status code 205 or exception if any
        """
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class LogoutAllView(APIView):
    """
    View to in validate all the tokens for the given user id. Only authenticated user can access this endpoint
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        This method finds all the outstanding tokens for current user id and one by one blacklists them
        Input:
            request => incoming request object
        Output:
            HTTP status code 205
        """
        tokens = OutstandingToken.objects.filter(user_id=request.user.id)
        for token in tokens:
            t, _ = BlacklistedToken.objects.get_or_create(token=token)

        return Response(status=status.HTTP_205_RESET_CONTENT)
