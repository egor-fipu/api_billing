from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from billing.models import Account
from .serializers import (CreateAccountSerializer, BalanceAccountSerializer,
                          TransactionSerializer)


class APICreateAccount(APIView):

    def post(self, request):
        serializer = CreateAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {
            'identifier': serializer.data.get('identifier')
        }
        return Response(data=data, status=status.HTTP_200_OK)


class APIBalanceAccount(APIView):

    def post(self, request):
        serializer = BalanceAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = get_object_or_404(
            Account,
            identifier=serializer.validated_data['identifier']
        )
        data = {
            'balance': account.balance
        }
        return Response(data=data, status=status.HTTP_200_OK)


class APITransaction(APIView):

    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        donor = serializer.validated_data['donor']
        recipient = serializer.validated_data['recipient']
        amount = serializer.validated_data['amount']
        if not donor.overdraft and donor.balance < amount:
            data = {
                'message': 'На Вашем счете недостаточно средств'
            }
            return Response(data=data, status=status.HTTP_409_CONFLICT)
        donor.balance -= amount
        recipient.balance += amount
        donor.save()
        recipient.save()
        serializer.save()
        data = {
            'message': f'Перевод осуществлен. '
                       f'Баланс счета-донора: {donor.balance}'
        }
        return Response(data=data, status=status.HTTP_200_OK)
