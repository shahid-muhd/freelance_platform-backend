from rest_framework import serializers
from .models import Portfolio
import json


class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = "__all__"


class WorkProfileSerializer:
    def serialize(self, query_data):
        json_data = []
        i = 0
        for item in query_data:
            json_data.append(
                {
                    "id": str(item.id),
                    "listing_id": i,
                    "title": item.title,
                    "description": item.description,
                    "skills": item.skills,
                    "user": item.user,
                }
            )
            i += 1
        return json.dumps(json_data)
