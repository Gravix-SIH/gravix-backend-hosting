from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    actor_email = serializers.SerializerMethodField()
    actor_name = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "actor",
            "actor_email",
            "actor_name",
            "action",
            "target_type",
            "target_id",
            "details",
            "ip_address",
            "user_agent",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp"]

    def get_actor_email(self, obj):
        return obj.actor.email if obj.actor else "System"

    def get_actor_name(self, obj):
        return obj.actor.name if obj.actor else "System"
