from rest_framework import serializers
from .models import Project, SavedProjects, Proposals
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from payments.models import Subscription


class ProjectSerializer(serializers.ModelSerializer):
    is_saved = serializers.SerializerMethodField()

    class Meta:
        model = Project
        exclude = ("is_blocked", "is_verified")
        extra_kwargs = {
            "client": {"read_only": True},
            "freelancer": {"read_only": True},
        }

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["client"] = user
        subscription = Subscription.objects.get(user_id=user.id, is_active=True)
        projects_left = subscription.projects_left
        if projects_left > 0:
            subscription.projects_left = projects_left - 1
            subscription.save()
            return Project.objects.create(**validated_data)
        return IndexError

    def get_is_saved(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            is_project_saved = SavedProjects.objects.filter(
                user=request.user, project=obj
            ).exists()

            return is_project_saved
        return False


class ProposalSerializer(serializers.ModelSerializer):
    project_title = serializers.SerializerMethodField()
    freelancer_name = serializers.SerializerMethodField()
    accepted_work = serializers.SerializerMethodField()

    class Meta:
        model = Proposals
        fields = "__all__"
        extra_kwargs = {"applicant": {"read_only": True}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If creating a new instance, exclude the 'status' field
        if self.instance is None:
            self.fields.pop("status")

    def get_project_title(self, obj):
        return obj.project.title

    def get_freelancer_name(self, obj):
        return obj.applicant.first_name + " " + obj.applicant.last_name

    def get_accepted_work(self, obj):
        accepted_work = None
        if obj.project.is_sample_completed:
            accepted_work = "sample"
        if obj.project.is_final_completed:
            accepted_work = "final"
         
        return accepted_work

    def create(self, validated_data):
        user = self.context["request"].user
        project_id = validated_data.get("project").id
        project_client = get_object_or_404(
            Project.objects.values("client"), id=project_id
        )

        if project_client["client"] == user.id:
            raise ValidationError("Cannot create proposal for your own project.")

        if Proposals.objects.filter(
            project_id=project_id, applicant_id=user.id
        ).exists():
            raise ValidationError("You have already proposed for this project.")

        validated_data["applicant"] = user

        return Proposals.objects.create(**validated_data)


class SavedProjectSerializer(serializers.ModelSerializer):

    class meta:
        model = SavedProjects
        fields = ("user", "project")
