from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.models import Role
from accounts.serializers import UserSerializer
from breatheesg.permissions import IsAdmin
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.get(username=request.data.get("username"))
            return Response(
                {
                    "success": True,
                    "data": {
                        "access": response.data["access"],
                        "refresh": response.data["refresh"],
                        "user": UserSerializer(user).data,
                    },
                }
            )
        return response


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"success": True, "data": UserSerializer(request.user).data})


class UserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        users = User.objects.select_related("client").all()
        return Response({"success": True, "data": UserSerializer(users, many=True).data})


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        from django.db import connection

        db_ok = True
        try:
            connection.ensure_connection()
        except Exception:
            db_ok = False
        return Response({"status": "ok", "database": "connected" if db_ok else "unavailable"})
