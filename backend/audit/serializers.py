from rest_framework import serializers

from audit.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    record_description = serializers.CharField(source="record.description", read_only=True, default="")
    performed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "record",
            "record_description",
            "action",
            "performed_by_name",
            "performed_at",
            "before_state",
            "after_state",
            "message",
        ]

    def get_performed_by_name(self, obj):
        if obj.performed_by:
            return obj.performed_by.get_full_name() or obj.performed_by.username
        return "System"
