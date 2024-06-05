from .models import CustomUser, Address
from rest_framework import serializers
from projects.models import Project


class UserRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ["email", "password", "first_name", "last_name"]
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


class UserSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()  # Adding read-only id field
    projects_listed = serializers.SerializerMethodField()
    projects_working = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "profile_image",
            "projects_listed",
            "projects_working",
        )
        # extra_kwargs = {
        #     "projects_listed": {"read_only": True},
        #     "projects_working": {"read_only": True},
        # }

    def get_projects_listed(self, instance):

        listed_project_count = Project.objects.filter(
            client_id=instance.id, is_archived=False
        ).count()
        return listed_project_count

    def get_projects_working(self, instance):

        working_project_count = Project.objects.filter(
            freelancer_id=instance.id
        ).count()
        return working_project_count


class Addressserializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"
