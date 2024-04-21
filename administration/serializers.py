from rest_framework import serializers
from accounts.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
        



class EmptySerializer(serializers.Serializer):
    pass
