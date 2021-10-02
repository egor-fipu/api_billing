from django.contrib import admin

from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'overdraft',
        'identifier',
        'balance',
        'created',
    )
    empty_value_display = '-пусто-'
