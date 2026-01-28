from rest_framework.serializers import ModelSerializer
from .models import SemicolonUserModel
from django.conf import settings

class SemiColonUserModelSerializer(ModelSerializer):
    class Meta:
        model = SemicolonUserModel
        fields = [
            "userId",
            "username",
            "email",
            "password",

        ]

    def create(self, validated_data):
        user =SemicolonUserModel.objects.create_user(
            validated_data["username"],
            validated_data["email"],
            validated_data["password"]
        )

        return user
