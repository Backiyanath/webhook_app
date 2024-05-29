# from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from django.shortcuts import get_object_or_404
from .models import Account, Destination
from .serializers import AccountSerializer, DestinationSerializer
import requests


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer

    def get_queryset(self):
        account_id = self.request.query_params.get('account_id', None)
        if account_id:
            return Destination.objects.filter(account__account_id=account_id)
        return super().get_queryset()


@api_view(['POST'])
def incoming_data(request):
    app_secret_token = request.headers.get('CL-X-TOKEN')
    if not app_secret_token:
        return Response({"error": "Un Authenticate"}, status=status.HTTP_401_UNAUTHORIZED)

    account = get_object_or_404(Account, app_secret_token=app_secret_token)
    data = request.data

    for destination in account.destinations.all():
        headers = destination.headers
        if destination.http_method == 'GET':
            response = requests.get(destination.url, headers=headers, params=data)
        elif destination.http_method in ['POST', 'PUT']:
            response = requests.request(destination.http_method, destination.url, headers=headers, json=data)

    return Response({"status": "Data sent successfully"}, status=status.HTTP_200_OK)
