from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.users.permissions import HasPermission


class PublicInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        _ = self.permission_classes
        return Response({
            "message": "Это публичная информация. Ее могут видеть все."
        })


class UserDocumentListView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permissions = ['view_own_documents']

    def get(self, request):
        _ = self.required_permissions
        return Response({
            "message": f"Привет, {request.user.email}! Здесь список твоих личных документов.",
            "documents": [
                {"id": 1, "title": "Мой первый документ"},
                {"id": 2, "title": "Мой секретный план"},
            ]
        })


class AdminReportView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permissions = ['view_financial_reports']

    def get(self, request):
        _ = self.required_permissions
        return Response({
            "message": "Это строго конфиденциальный финансовый отчет.",
            "report": {
                "year": 2025,
                "revenue": "1,000,000 USD",
                "profit": "200,000 USD"
            }
        })
