from django.db.models import Count, Q, Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from audit.models import AuditAction, AuditLog, ApprovalRecord
from breatheesg.exceptions import BusinessLogicError
from emissions.models import NormalizedRecord, ReviewStatus
from emissions.serializers import NormalizedRecordSerializer


def _client_queryset(user):
    qs = NormalizedRecord.objects.select_related("emission_factor", "reviewed_by", "raw_record")
    if user.role != "ADMIN" and user.client_id:
        qs = qs.filter(client_id=user.client_id)
    return qs


class RecordViewSet(ReadOnlyModelViewSet):
    serializer_class = NormalizedRecordSerializer

    def get_queryset(self):
        qs = _client_queryset(self.request.user)
        params = self.request.query_params
        if status_filter := params.get("review_status"):
            qs = qs.filter(review_status=status_filter)
        if source := params.get("source_type"):
            qs = qs.filter(source_type=source)
        if scope := params.get("scope"):
            qs = qs.filter(scope=scope)
        if search := params.get("search"):
            qs = qs.filter(description__icontains=search)
        return qs

    def _state(self, record):
        return {
            "review_status": record.review_status,
            "is_locked": record.is_locked,
            "emission_kgco2e": str(record.emission_kgco2e or ""),
        }

    def _transition(self, record, new_status, user, action):
        if record.is_locked:
            raise BusinessLogicError("Record is locked and cannot be modified.")
        before = self._state(record)
        record.review_status = new_status
        record.reviewed_by = user
        record.reviewed_at = timezone.now()
        if new_status == ReviewStatus.APPROVED:
            record.is_locked = True
        record.save()
        AuditLog.objects.create(
            record=record,
            action=action,
            performed_by=user,
            before_state=before,
            after_state=self._state(record),
        )
        if new_status == ReviewStatus.APPROVED:
            ApprovalRecord.objects.create(record=record, approved_by=user)
        return record

    @action(detail=True, methods=["patch"], url_path="approve")
    def approve(self, request, pk=None):
        record = self.get_object()
        if record.review_status == ReviewStatus.APPROVED and record.is_locked:
            raise BusinessLogicError("Record is already approved and locked.")
        self._transition(record, ReviewStatus.APPROVED, request.user, AuditAction.APPROVED)
        return Response({"success": True, "data": NormalizedRecordSerializer(record).data})

    @action(detail=True, methods=["patch"], url_path="flag")
    def flag(self, request, pk=None):
        record = self.get_object()
        self._transition(record, ReviewStatus.FLAGGED, request.user, AuditAction.FLAGGED)
        return Response({"success": True, "data": NormalizedRecordSerializer(record).data})

    @action(detail=True, methods=["patch"], url_path="reject")
    def reject(self, request, pk=None):
        record = self.get_object()
        self._transition(record, ReviewStatus.REJECTED, request.user, AuditAction.REJECTED)
        return Response({"success": True, "data": NormalizedRecordSerializer(record).data})

    @action(detail=False, methods=["patch"], url_path="bulk-approve")
    def bulk_approve(self, request):
        ids = request.data.get("ids", [])
        if not ids:
            raise BusinessLogicError("No record IDs provided.")
        updated = []
        for record in self.get_queryset().filter(id__in=ids, is_locked=False):
            self._transition(record, ReviewStatus.APPROVED, request.user, AuditAction.BULK_APPROVED)
            updated.append(record.id)
        return Response({"success": True, "approved_ids": updated, "count": len(updated)})


class RecordStatsView(APIView):
    def get(self, request):
        qs = _client_queryset(request.user)
        agg = qs.aggregate(
            total=Count("id"),
            pending=Count("id", filter=Q(review_status=ReviewStatus.PENDING)),
            approved=Count("id", filter=Q(review_status=ReviewStatus.APPROVED)),
            flagged=Count("id", filter=Q(review_status=ReviewStatus.FLAGGED)),
            total_emissions=Sum("emission_kgco2e"),
        )
        by_scope = (
            qs.values("scope")
            .annotate(count=Count("id"), emissions=Sum("emission_kgco2e"))
            .order_by("scope")
        )
        recent = qs.order_by("-created_at")[:10]
        return Response(
            {
                "success": True,
                "data": {
                    "summary": {
                        "total": agg["total"] or 0,
                        "pending": agg["pending"] or 0,
                        "approved": agg["approved"] or 0,
                        "flagged": agg["flagged"] or 0,
                        "total_emissions_kgco2e": float(agg["total_emissions"] or 0),
                    },
                    "by_scope": list(by_scope),
                    "recent": NormalizedRecordSerializer(recent, many=True).data,
                },
            }
        )
