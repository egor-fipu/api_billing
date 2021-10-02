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
Ответ
```
{
    "message": "Перевод осуществлен. Баланс счета-донора: -2200.0"
}
```
или
```
{
    "message": "На Вашем счете недостаточно средств"
}
```