from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer class for registering users
    
    """
    #make sure email is a valid field and unique
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )

    #validates the password against the django password requirements
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirmpassword = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'confirmpassword', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        """
        Method to validate if entered password and confirm password matches or not.
        Input:
            attrs ==> dictionary that represents user input
        Output:
            validation error if any else simply returns the input
        """
        if attrs['password'] != attrs['confirmpassword']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        """
        Method to create the user.
        Input:
            validated_data ==> input data that meets the necessary validations.
        Output:
            user object (new user that just got created)
        """
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class ChangePasswordSerializer(serializers.ModelSerializer):
    """
    Serializer to change password of existing user

    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirmpassword = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('old_password', 'password', 'confirmpassword')

    def validate(self, attrs):
        """
        Method to validate if entered password and confirm password matches or not.
        Input:
            attrs ==> dictionary that represents user input
        Output:
            validation error if any else simply returns the input
        """
        if attrs['password'] != attrs['confirmpassword']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def validate_old_password(self, value):
        """
        Method to validate if entered old password matches with the record in database or not
        Input:
            value ==> respresents old password
        Output:
            validation error if any else simply returns the input
        """
        #check_password is used as we don't store user password in plain text
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):
        """
        Method to update the passwords
        Input:
            instance ==> current user instance
            validated_data ==> input data that meets the necessary validations.
        Output:
            instance (with password updated)
        """
        user = self.context['request'].user
        #to ensure current user is the one trying to change his/her own password
        if user.pk != instance.pk:
            raise serializers.ValidationError({"authorize": "You dont have permission for this user."})

        instance.set_password(validated_data['password'])
        instance.save()

        return instance


class UpdateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    """
    Serializer class to update user profile.
    """
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate_email(self, value):
        """
        Method to validate email to ensure new email entered by user does not already exists.
        Input:
            value ==> email entered by user
        Output:
            same as input if no validation error else validation error
        """
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError({"email": "This email is already in use."})
        return value

    def validate_username(self, value):
        """
        Method to validate username to ensure new username entered by user does not already exists.
        Input:
            value ==>  username entered by user
        Output:
            same as input if no validation error else validation error
        """
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError({"username": "This username is already in use."})
        return value

    def update(self, instance, validated_data):
        """
        Method to update the passwords
        Input:
            instance ==> current user instance
            validated_data ==> input data that meets the necessary validations.
        Output:
            instance (with username and/or email updated)
        """
        user = self.context['request'].user

        #to ensure current user is the one trying to change his/her own password
        if user.pk != instance.pk:
            raise serializers.ValidationError({"authorize": "You dont have permission for this user."})

        instance.first_name = validated_data['first_name']
        instance.last_name = validated_data['last_name']
        instance.email = validated_data['email']
        instance.username = validated_data['username']

        instance.save()

        return instance
