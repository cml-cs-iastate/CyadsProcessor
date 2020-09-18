from rest_framework import serializers
from .models import Batch, Locations


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Locations
        fields = "__all__"


class BatchSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    location = LocationSerializer(many=False, read_only=True)
    start_datetime = serializers.DateTimeField(read_only=True)
    completed_datetime = serializers.DateTimeField(read_only=True)


    class Meta:
        model = Batch

        fields = (
            'id', 'start_timestamp', 'completed_timestamp', 'time_taken',
            "total_bots", "external_ip", "status", "video_list_size",
            'server_hostname', 'server_container', 'location', 'synced', 'processed',
            "start_datetime", "completed_datetime",
        )
