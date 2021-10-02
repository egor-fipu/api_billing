from rest_framework import serializers

from billing.models import Account, Transaction


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
