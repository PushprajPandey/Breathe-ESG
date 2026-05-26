from rest_framework import serializers

from emissions.models import NormalizedRecord


class NormalizedRecordSerializer(serializers.ModelSerializer):
    emission_factor_name = serializers.CharField(
        source="emission_factor.category", read_only=True, default=""
    )
    reviewed_by_name = serializers.SerializerMethodField()
    raw_data = serializers.SerializerMethodField()
    parse_status = serializers.SerializerMethodField()
    parse_error = serializers.SerializerMethodField()
    upload_id = serializers.SerializerMethodField()
    row_number = serializers.SerializerMethodField()

    class Meta:
        model = NormalizedRecord
        fields = [
            "id",
            "source_type",
            "raw_data",
            "parse_status",
            "parse_error",
            "upload_id",
            "row_number",
            "activity_date",
            "description",
            "quantity",
            "unit",
            "normalized_quantity_kwh",
            "emission_kgco2e",
            "scope",
            "review_status",
            "reviewed_by",
            "reviewed_by_name",
            "reviewed_at",
            "is_locked",
            "emission_factor_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_reviewed_by_name(self, obj):
        if obj.reviewed_by:
            return obj.reviewed_by.get_full_name() or obj.reviewed_by.username
        return None

    def get_raw_data(self, obj):
        if obj.raw_record_id and hasattr(obj, "raw_record") and obj.raw_record:
            return obj.raw_record.raw_data
        return {}

    def get_parse_status(self, obj):
        if hasattr(obj, "raw_record") and obj.raw_record:
            return obj.raw_record.parse_status
        return None

    def get_parse_error(self, obj):
        if hasattr(obj, "raw_record") and obj.raw_record:
            return obj.raw_record.parse_error
        return ""

    def get_upload_id(self, obj):
        if hasattr(obj, "raw_record") and obj.raw_record:
            return obj.raw_record.upload_id
        return None

    def get_row_number(self, obj):
        if hasattr(obj, "raw_record") and obj.raw_record:
            return obj.raw_record.row_number
        return None
