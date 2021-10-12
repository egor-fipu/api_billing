from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from billing.models import Account
from .mixins import CreateViewSet
from .serializers import (CreateAccountSerializer, BalanceAccountSerializer,
                          TransactionSerializer, UserSerializer,
                          UserGetTokenSerializer)
from .services import user_transaction

User = get_user_model()


class UserViewSet(CreateViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'], url_path='token')
    def get_token(self, request):
        serializer = UserGetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User, username=serializer.validated_data['username']
        )
        if user.check_password(serializer.validated_data['password']):
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)
            data = {
                'token': token
            }
            return Response(data=data, status=status.HTTP_200_OK)
        raise serializers.ValidationError({'password': 'Неверный пароль'})


class APICreateAccount(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = CreateAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=self.request.user)
        data = {
            'identifier': serializer.data.get('identifier')
        }
        return Response(data=data, status=status.HTTP_200_OK)


class APIBalanceAccount(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = BalanceAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = get_object_or_404(
            Account,
            identifier=serializer.validated_data['identifier'],
            owner=self.request.user
        )
        data = {
            'balance': account.balance
        }
        return Response(data=data, status=status.HTTP_200_OK)


class APITransaction(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = TransactionSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        donor = serializer.validated_data['donor']
        recipient = serializer.validated_data['recipient']
        amount = serializer.validated_data['amount']
        result = user_transaction(donor, recipient, amount)
        serializer.save()
        return Response(**result)
