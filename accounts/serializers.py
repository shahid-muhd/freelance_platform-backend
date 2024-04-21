from .models import CustomUser,Address
from rest_framework import serializers


class UserRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ["email", "password","first_name","last_name"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = CustomUser.objects.create(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
         
        )
        user.set_password(validated_data["password"])
        user.save()
        return user




class Userserializer(serializers.ModelSerializer):
        class Meta:
            model = CustomUser
            fields = ('first_name', 'last_name', 'email','phone')

class Addressserializer(serializers.ModelSerializer):
        class Meta:
            model = Address
            fields = '__all__'