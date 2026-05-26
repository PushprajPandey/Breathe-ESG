from rest_framework import serializers

from ingestion.models import FileUpload, RawRecord


class FileUploadSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()
    filename = serializers.SerializerMethodField()

    class Meta:
        model = FileUpload
        fields = [
            "id",
            "source_type",
            "uploaded_at",
            "status",
            "rows_parsed",
            "rows_failed",
            "rows_suspicious",
            "rows_truncated",
            "filename",
            "uploaded_by_name",
        ]

    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return obj.uploaded_by.username
        return None

    def get_filename(self, obj):
        if obj.file_path:
            return obj.file_path.name.split("/")[-1]
        return ""


class RawRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawRecord
        fields = [
            "id",
            "row_number",
            "parse_status",
            "parse_error",
            "raw_data",
            "created_at",
        ]
