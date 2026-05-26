from rest_framework.generics import ListAPIView

from breatheesg.permissions import IsAdmin
from tenants.models import Client
from tenants.serializers import ClientSerializer


class ClientListView(ListAPIView):
    permission_classes = [IsAdmin]
    serializer_class = ClientSerializer
    queryset = Client.objects.all()
