import uuid

from django.db import models


class Account(models.Model):
    SAVINGS = 'savings'
    PAYMENT = 'payment'
    CURRENT = 'current'
    ACCOUNT_NAMES = [
        (SAVINGS, 'сберегательный'),
        (PAYMENT, 'расчетный'),
        (CURRENT, 'текущий'),
    ]

    name = models.CharField(
        'Название',
        max_length=7,
        choices=ACCOUNT_NAMES
    )
    overdraft = models.BooleanField('Овердрафтность')
    identifier = models.CharField(
        'Идентификатор',
        editable=False,
        max_length=36,
        default=uuid.uuid4,
        unique=True,
    )
    balance = models.FloatField('Остаток на счете', default=0)
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Счет'
        verbose_name_plural = 'Счета'
        ordering = ['-created']

    def __str__(self):
        return self.identifier


class Transaction(models.Model):
    donor = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        related_name='donor_transactions',
        verbose_name='Счет-донор'
    )
    recipient = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recipient_transactions',
        verbose_name='Счет-реципиент'
    )
    amount = models.FloatField('Сумма перевода')
    created = models.DateTimeField(
        'Дата операции',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'
        ordering = ['-created']

    def __str__(self):
        return f'{self.donor}, {self.recipient}'
