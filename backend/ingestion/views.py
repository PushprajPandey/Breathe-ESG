from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from ingestion.models import FileUpload, ParseStatus, RawRecord, SourceType
from ingestion.pipeline import process_upload
from ingestion.serializers import FileUploadSerializer, RawRecordSerializer
from tenants.models import Client


def _upload_queryset(user):
    qs = FileUpload.objects.select_related("uploaded_by")
    if user.role != "ADMIN" and user.client_id:
        qs = qs.filter(client_id=user.client_id)
    return qs


class UploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, source_type):
        source_map = {"sap": SourceType.SAP, "utility": SourceType.UTILITY, "travel": SourceType.TRAVEL}
        if source_type not in source_map:
            return Response(
                {"success": False, "error": {"code": "invalid_source", "message": "Invalid source type"}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response(
                {"success": False, "error": {"code": "missing_file", "message": "No file uploaded"}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        client = request.user.client
        if not client:
            client = Client.objects.first()
        if not client:
            return Response(
                {"success": False, "error": {"code": "no_client", "message": "No client configured"}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        upload = FileUpload.objects.create(
            client=client,
            source_type=source_map[source_type],
            uploaded_by=request.user,
            file_path=file_obj,
        )
        process_upload(upload, user=request.user)
        issues = RawRecord.objects.filter(
            upload=upload, parse_status__in=[ParseStatus.FAILED, ParseStatus.SUSPICIOUS]
        ).count()
        data = FileUploadSerializer(upload).data
        data["issues_count"] = issues
        return Response({"success": True, "data": data}, status=status.HTTP_201_CREATED)


class UploadListView(ListAPIView):
    serializer_class = FileUploadSerializer
    pagination_class = None

    def get_queryset(self):
        qs = _upload_queryset(self.request.user)
        if source := self.request.query_params.get("source_type"):
            qs = qs.filter(source_type=source)
        return qs[:20]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({"success": True, "data": response.data})


class UploadIssuesView(RetrieveAPIView):
    """Failed and suspicious raw rows for an upload — analyst can see what broke."""

    def get_queryset(self):
        return _upload_queryset(self.request.user)

    def retrieve(self, request, *args, **kwargs):
        upload = self.get_object()
        status_filter = request.query_params.get("parse_status")
        qs = upload.raw_records.all()
        if status_filter:
            qs = qs.filter(parse_status=status_filter)
        else:
            qs = qs.filter(parse_status__in=[ParseStatus.FAILED, ParseStatus.SUSPICIOUS])
        return Response(
            {
                "success": True,
                "data": {
                    "upload": FileUploadSerializer(upload).data,
                    "issues": RawRecordSerializer(qs[:200], many=True).data,
                },
            }
        )
