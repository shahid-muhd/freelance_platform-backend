from rest_framework import serializers
from .models import Project
from django.contrib.auth.models import User


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"
        extra_kwargs = {'client': {'read_only': True}}

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def create(self, validated_data):
        validated_data["client"] = self.context["request"].user
        return Project.objects.create(**validated_data)
