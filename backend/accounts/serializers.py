from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Address, User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "phone"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "phone"]
        read_only_fields = ["id", "username"]


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["id", "label", "line1", "line2", "city", "state", "zip_code", "is_default"]

    def create(self, validated_data):
        # Identity comes from the authenticated request, never the payload.
        return Address.objects.create(user=self.context["request"].user, **validated_data)
