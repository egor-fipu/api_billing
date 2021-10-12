from django.contrib.auth import get_user_model
from rest_framework import serializers

from billing.models import Account, Transaction

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserGetTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150, validators=[])

    class Meta:
        model = User
        fields = ('username', 'password')


class CreateAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('name', 'overdraft', 'identifier')
        read_only_fields = ('identifier',)


class BalanceAccountSerializer(serializers.ModelSerializer):
    identifier = serializers.CharField(max_length=36, validators=[])

    class Meta:
        model = Account
        fields = ('identifier',)


class TransactionSerializer(serializers.ModelSerializer):
    donor = serializers.SlugRelatedField(
        slug_field='identifier', queryset=Account.objects.all()
    )
    recipient = serializers.SlugRelatedField(
        slug_field='identifier', queryset=Account.objects.all()
    )

    class Meta:
        model = Transaction
        fields = ('donor', 'recipient', 'amount')

    def validate(self, data):
        donor = data.get('donor')
        recipient = data.get('recipient')
        amount = data.get('amount')
        user = self.context['request'].user
        if donor.owner != user:
            raise serializers.ValidationError({
                'donor': 'Вы можете переводить средства только со своего счета'
            })
        if donor == recipient:
            raise serializers.ValidationError({
                'recipient': 'Счета "donor" и "recipient" не должны быть одинаковыми'
            })
        if not donor.overdraft and donor.balance < amount:
            raise serializers.ValidationError({
                'amount': 'На Вашем счете недостаточно средств'
            })
        return data
