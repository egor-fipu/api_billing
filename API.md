### Регистрация
POST-запрос /api/v1/auth/
```
{
    "username": "user_1",
    "password": "test_password"
}
```
Ответ
```
{
    "username": "user_1"
}
```

### Получение токена
POST-запрос /api/v1/auth/token/
```
{
    "username": "user_1",
    "password": "test_password"
}
```
Ответ
```
{
    "token": "string"
}
```
Этот токен необходимо передавать в заголовке каждого запроса, в поле 
Authorization. Перед токеном должно стоять ключевое слово Bearer и пробел

### Создание счета
POST-запрос /api/v1/accounts/create/
```
{
    "name": "payment",
    "overdraft": false
}
```
Ответ
```
{
    "identifier": "dfe692a7-598e-44e4-9d6f-8e27b2e71c31"
}
```

### Запрос баланса счета
POST-запрос /api/v1/accounts/balance/
```
{
    "identifier": "a469ec7d-3d3b-4579-a10c-2e1ae31c44ea"
}
```
Ответ
```
{
    "balance": 0.0
}
```

### Перевод денег со счета А на счет В
POST-запрос /api/v1/accounts/transaction/
```
{
    "donor": "5b83d7b8-46a9-49c3-86a1-b0d9d887030u",
    "recipient": "ed0873d3-b202-4246-bbe9-40cce328bab3",
    "amount": 100
}
```
Варианты ответов:
```
{
    "message": "Перевод осуществлен. Баланс счета-донора: -2200.0"
}
```
```
{
    "amount": [
        "На Вашем счете недостаточно средств"
    ]
}
```
```
{
    "donor": [
        "Вы можете переводить средства только со своего счета"
    ]
}
```
```
{
    "recipient": [
        "Счета \"donor\" и \"recipient\" не должны быть одинаковыми"
    ]
}
```