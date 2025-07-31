from django.urls import path

from .views import AdminReportView, PublicInfoView, UserDocumentListView

urlpatterns = [
    path("public/", PublicInfoView.as_view(), name="public-info"),
    path("docs/my/", UserDocumentListView.as_view(), name="user-documents"),
    path("reports/financial/", AdminReportView.as_view(), name="admin-report"),
]
