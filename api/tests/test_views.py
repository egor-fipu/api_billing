from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from billing.models import Account, Transaction

User = get_user_model()


class AuthTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data = {
            'username': 'test_user',
            'password': 'test_password',
        }
        cls.create_user_url = '/api/v1/auth/'
        cls.get_token_url = '/api/v1/auth/token/'

    def test_create_account(self):
        response = self.client.post(
            self.create_user_url, self.data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(
            User.objects.filter(
                username=self.data['username']
            ).exists()
        )
        self.assertEqual(response.data.get('username'), self.data['username'])

        response = self.client.post(
            self.create_user_url,
            self.data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(
            response.data.get('username'),
            ['A user with that username already exists.']
        )

        empty_data = {
            'username': '',
            'password': ''
        }
        response = self.client.post(
            self.create_user_url,
            empty_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        json = response.json()
        for field, message in json.items():
            with self.subTest(field):
                self.assertEqual(message, ['This field may not be blank.'])

        empty_data = {}
        response = self.client.post(
            self.create_user_url, empty_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        json = response.json()
        for field, message in json.items():
            with self.subTest(field):
                self.assertEqual(message, ['This field is required.'])

    def test_get_token(self):
        self.client.post(self.create_user_url, self.data, format='json')
        response = self.client.post(
            self.get_token_url,
            {
                'username': self.data['username'],
                'password': self.data['password'],
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.json())

        invalid_data = {
            'username': 'invalid_username',
            'password': 'test_password'
        }
        response = self.client.post(
            self.get_token_url, invalid_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get('detail'), 'Not found.')

        invalid_data = {
            'username': self.data['username'],
            'password': 'invalid_password'
        }
        response = self.client.post(
            self.get_token_url, invalid_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('password'), 'Неверный пароль')


class AccountsTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.create_url = '/api/v1/accounts/create/'
        cls.balance_url = '/api/v1/accounts/balance/'
        cls.transaction_url = '/api/v1/accounts/transaction/'

        cls.user_1 = User.objects.create(
            username='test_user_1',
        )
        cls.user_2 = User.objects.create(
            username='test_user_2'
        )
        cls.account_1 = Account.objects.create(
            owner=cls.user_1,
            name=Account.PAYMENT,
            overdraft=False,
            balance=1000
        )
        cls.account_2 = Account.objects.create(
            owner=cls.user_2,
            name=Account.SAVINGS,
            overdraft=True,
            balance=500
        )

    def setUp(self):
        refresh = RefreshToken.for_user(self.user_1)
        token = str(refresh.access_token)
        self.authorized_client = APIClient()
        self.authorized_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )

    def test_create_account(self):
        valid_data = {
            'name': 'current',
            'overdraft': False
        }
        response = self.authorized_client.post(
            self.create_url, valid_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('identifier' in response.data)
        self.assertTrue(
            Account.objects.filter(
                owner=self.user_1,
                identifier=response.data.get('identifier'),
                name=valid_data['name'],
                overdraft=valid_data['overdraft']
            ).exists()
        )

        invalid_data = {
            'name': 'invalid',
            'overdraft': False
        }
        response = self.authorized_client.post(
            self.create_url, invalid_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        invalid_data = {
            'name': 'current'
        }
        response = self.authorized_client.post(
            self.create_url, invalid_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_balance_account(self):
        valid_data = {
            'identifier': self.account_1.identifier
        }
        response = self.authorized_client.post(
            self.balance_url, valid_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('balance' in response.data)
        self.assertEqual(self.account_1.balance, response.data.get('balance'))

        invalid_data = {
            'identifier': 'invalid_identifier'
        }
        response = self.authorized_client.post(
            self.balance_url, invalid_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        invalid_data = {
            'identifier': ''
        }
        response = self.authorized_client.post(
            self.balance_url, invalid_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_transaction_account(self):
        subtests_tuple = (
            (
                {
                    'donor': self.account_1.identifier,
                    'recipient': self.account_2.identifier,
                    'amount': 1100
                },
                'amount',
                ['На Вашем счете недостаточно средств']
            ),
            (
                {
                    'donor': self.account_2.identifier,
                    'recipient': self.account_1.identifier,
                    'amount': 1100
                },
                'donor',
                ['Вы можете переводить средства только со своего счета']
            ),
            (
                {
                    'donor': self.account_1.identifier,
                    'recipient': self.account_1.identifier,
                    'amount': 1100
                },
                'recipient',
                ['Счета "donor" и "recipient" не должны быть одинаковыми']
            )
        )
        for data, field, message in subtests_tuple:
            with self.subTest(message):
                response = self.authorized_client.post(
                    self.transaction_url, data, format='json'
                )
                self.assertEqual(
                    response.status_code, status.HTTP_400_BAD_REQUEST
                )
                self.assertTrue(field in response.data)
                self.assertEqual(response.data.get(field), message)
                self.assertEqual(Transaction.objects.count(), 0)

        valid_data = {
            'donor': self.account_1.identifier,
            'recipient': self.account_2.identifier,
            'amount': 900
        }
        response = self.authorized_client.post(
            self.transaction_url, valid_data, format='json'
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
            'donor': 'invalid_identifier',
            'recipient': 'invalid_identifier',
            'amount': 'xxx'
        }
        response = self.authorized_client.post(
            self.transaction_url, invalid_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        json = response.json()
        self.assertEqual(
            json['donor'],
            [f'Object with identifier={invalid_data["donor"]} does not exist.']
        )
        self.assertEqual(
            json['recipient'],
            ['Object with identifier='
             f'{invalid_data["recipient"]} does not exist.']
        )
        self.assertEqual(json['amount'], ['A valid number is required.'])

    def test_permissions(self):
        subtests_tuple = (
            (self.create_url, 'unauthorized create account'),
            (self.balance_url, 'unauthorized get balance'),
            (self.transaction_url, 'unauthorized post transaction'),
        )
        for address, subtest_description in subtests_tuple:
            with self.subTest(subtest_description):
                response = self.client.post(address)
                self.assertEqual(
                    response.status_code, status.HTTP_401_UNAUTHORIZED
                )

