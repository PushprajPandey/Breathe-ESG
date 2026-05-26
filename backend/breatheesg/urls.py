from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from accounts.views import HealthView, LoginView, MeView, UserListView
from audit.views import AuditExportView, AuditLogListView
from emissions.views import RecordStatsView, RecordViewSet
from ingestion.views import UploadIssuesView, UploadListView, UploadView
from tenants.views import ClientListView

router = DefaultRouter()
router.register(r"records", RecordViewSet, basename="records")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", HealthView.as_view()),
    path("api/auth/login/", LoginView.as_view(), name="token_obtain_pair"),
    path("api/auth/me/", MeView.as_view()),
    path("api/users/", UserListView.as_view()),
    path("api/clients/", ClientListView.as_view()),
    path("api/upload/<str:source_type>/", UploadView.as_view()),
    path("api/uploads/", UploadListView.as_view()),
    path("api/uploads/<int:pk>/issues/", UploadIssuesView.as_view()),
    path("api/records/stats/", RecordStatsView.as_view()),
    path("api/audit-log/", AuditLogListView.as_view()),
    path("api/audit-log/export/", AuditExportView.as_view()),
    path("api/", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
