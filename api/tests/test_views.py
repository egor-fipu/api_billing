from rest_framework import status
from rest_framework.test import APITestCase

from billing.models import Account, Transaction


class ViewsTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.domain = 'http://127.0.0.1:8000/'
        cls.create = f'{cls.domain}api/v1/accounts/create/'
        cls.balance = f'{cls.domain}api/v1/accounts/balance/'
        cls.transaction = f'{cls.domain}api/v1/accounts/transaction/'

        cls.account_1 = Account.objects.create(
            name=Account.PAYMENT,
            overdraft=True,
            balance=1000
        )
        cls.account_2 = Account.objects.create(
            name=Account.SAVINGS,
            overdraft=False,
            balance=500
        )

    def test_create_account(self):
        valid_data = {
            'name': 'current',
            'overdraft': False
        }
        response = self.client.post(self.create, valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('identifier' in response.data)
        self.assertTrue(
            Account.objects.filter(
                identifier=response.data.get('identifier'),
                name=valid_data['name'],
                overdraft=valid_data['overdraft']
            ).exists()
        )

        invalid_data = {
            'name': 'invalid',
            'overdraft': False
        }
        response = self.client.post(self.create, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        invalid_data = {
            'name': 'current'
        }
        response = self.client.post(self.create, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_balance_account(self):
        valid_data = {
            'identifier': self.account_1.identifier
        }
        response = self.client.post(self.balance, valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('balance' in response.data)
        self.assertEqual(self.account_1.balance, response.data.get('balance'))

        invalid_data = {
            'identifier': 'a469ec7d-3d3b-4579-a10c-2e1ae31c44ea'
        }
        response = self.client.post(self.balance, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        invalid_data = {
            'identifier': ''
        }
        response = self.client.post(self.balance, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_transaction_account(self):
        valid_data = {
            'donor': self.account_2.identifier,
            'recipient': self.account_1.identifier,
            'amount': 600
        }
        response = self.client.post(
            self.transaction, valid_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue('message' in response.data)
        self.assertEqual(
            response.data.get('message'),
            'На Вашем счете недостаточно средств'
        )
        self.assertEqual(Transaction.objects.count(), 0)

        valid_data = {
            'donor': self.account_1.identifier,
            'recipient': self.account_2.identifier,
            'amount': 1100
        }
        response = self.client.post(
            self.transaction, valid_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('message' in response.data)
        self.assertEqual(
            Account.objects.get(identifier=self.account_1.identifier).balance,
            self.account_1.balance - valid_data['amount']
        )
        self.assertEqual(
            Account.objects.get(identifier=self.account_2.identifier).balance,
            self.account_2.balance + valid_data['amount']
        )
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertTrue(
            Transaction.objects.filter(
                donor=self.account_1,
                recipient=self.account_2,
                amount=valid_data['amount']
            ).exists()
        )

        invalid_data = {
            'donor': 'a469ec7d-3d3b-4579-a10c-2e1ae31c44ea',
            'recipient': self.account_2.identifier,
            'amount': 1100
        }
        response = self.client.post(
            self.transaction, invalid_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        invalid_data = {
            'donor': self.account_1.identifier,
            'recipient': self.account_2.identifier,
            'amount': 'xxx'
        }
        response = self.client.post(
            self.transaction, invalid_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
