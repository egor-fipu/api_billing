from rest_framework import status


def user_transaction(donor, recipient, amount):
    donor.balance -= amount
    recipient.balance += amount
    donor.save()
    recipient.save()
    result = {
        'data': {
            'message': f'Перевод осуществлен. Баланс Вашего счета: {donor.balance}'
        },
        'status': status.HTTP_200_OK
    }
    return result
