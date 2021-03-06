from wsgiref import validate
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.utils.translation import ugettext_lazy as _
from allauth.account import app_settings as allauth_settings
from allauth.account.forms import ResetPasswordForm
from allauth.utils import email_address_exists
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from rest_framework import serializers
from rest_auth.serializers import PasswordResetSerializer
import stripe
from django.conf import settings

from yearbook.models import YearbookCommittee

User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    in_committee = serializers.BooleanField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email","password","name","lname","username","dob","high_school","address","zip_code","status","photo","role","in_committee"]
        extra_kwargs = {
            "password": {"write_only": True, "style": {"input_type": "password"}},
            "status":{"read_only":True}
            }

    def _get_request(self):
        request = self.context.get("request")
        if (
            request
            and not isinstance(request, HttpRequest)
            and hasattr(request, "_request")
        ):
            request = request._request
        return request

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _("A user is already registered with this e-mail address.")
                )
        return email

    def validate_username(self, username):
        username = get_adapter().clean_email(username)
        if User.objects.filter(username=username):
            raise serializers.ValidationError(
                _("A user is already registered with this username.")
            )
        return username

        
    def create(self, validated_data):

        if(validated_data.get("role") == 1):
            if User.objects.filter(high_school=validated_data.get('high_school'),role=2).count() == 0:
                raise serializers.ValidationError(
                    _("Not admin found for this school")
                )
        
        if(validated_data.get("role") == 2):
           if validated_data.get("email").find(".edu") == -1:
                raise serializers.ValidationError(
                    _("Must be .edu email for school admins")
                ) 

        user = User(
            email=validated_data.get("email"),
            name=validated_data.get("name"),
            # username=generate_unique_username(
            #     [validated_data.get("name"), validated_data.get("email"), "user"]
            # ),
            username=validated_data.get("username"),
            lname=validated_data.get("lname"),
            dob=validated_data.get("dob"),
            high_school=validated_data.get("high_school"),
            address=validated_data.get("address"),
            zip_code=validated_data.get("zip_code"),
            role=validated_data.get("role"),
            status='pending'
        )
        
        user.set_password(validated_data.get("password"))
        stripe.api_key = settings.STRIPE_SECRET_KEY

        stripe_customer= stripe.Customer.create()
        user.stripe_id = stripe_customer.id

        user.save()

        if user.role == 1 and validated_data.get("in_committee") == True:
            YearbookCommittee.objects.create(user=user,high_school=user.high_school)

        request = self._get_request()
        setup_user_email(request, user, [])
        return user

    def save(self, request=None):
        """rest_auth passes request so we must override to accept it"""
        return super().save()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name","lname","username","dob","high_school","address","zip_code","status","photo","role","stripe_id"]
        


class PasswordSerializer(PasswordResetSerializer):
    """Custom serializer for rest_auth to solve reset password error"""

    password_reset_form_class = ResetPasswordForm