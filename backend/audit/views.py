import csv
import io

from django.http import HttpResponse
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from audit.models import AuditLog
from audit.serializers import AuditLogSerializer
from emissions.models import NormalizedRecord


class AuditLogListView(ListAPIView):
    serializer_class = AuditLogSerializer

    def get_queryset(self):
        qs = AuditLog.objects.select_related("record", "performed_by").order_by("-performed_at")
        user = self.request.user
        if user.role != "ADMIN" and user.client_id:
            qs = qs.filter(record__client_id=user.client_id)
        if action := self.request.query_params.get("action"):
            qs = qs.filter(action=action)
        return qs


class AuditExportView(APIView):
    def get(self, request):
        qs = NormalizedRecord.objects.filter(is_locked=True)
        if request.user.role != "ADMIN" and request.user.client_id:
            qs = qs.filter(client_id=request.user.client_id)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "id",
                "source_type",
                "activity_date",
                "description",
                "emission_kgco2e",
                "scope",
                "review_status",
            ]
        )
        for r in qs:
            writer.writerow(
                [
                    r.id,
                    r.source_type,
                    r.activity_date,
                    r.description,
                    r.emission_kgco2e,
                    r.scope,
                    r.review_status,
                ]
            )
        response = HttpResponse(output.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="audit_export.csv"'
        return response
