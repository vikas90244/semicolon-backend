from rest_framework import serializers
from .models import SemicolonUserModel


class SemicolonUserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SemicolonUserModel
        fields = ["userId", "username", "email"]
        read_only_fields = ["userId"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = SemicolonUserModel
        fields = ["email", "username", "password"]
    
    def create(self, validated_data):
        user = SemicolonUserModel.objects.create_user(
            email=validated_data["email"],
            username=validated_data.get("username", validated_data["email"].split('@')[0]),
            password=validated_data["password"]
        )
        return user
