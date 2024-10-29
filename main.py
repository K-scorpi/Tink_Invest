from tinkoff.invest import Client
from sec import token

TOKEN = token

def get_account_balance(token: str):
    with Client(token) as client:
        try:
            # Получение списка счетов
            accounts = client.users.get_accounts().accounts
            if not accounts:
                print("Счета не найдены.")
                return
            
            # Переменная для накопления общей суммы по всем счетам
            total_all_accounts = 0.0
            
            for account in accounts:
                print(f"Счет: {account.id}, тип: {account.type}")
                
                # Получение портфеля и позиций для расчета баланса по каждому счету
                portfolio = client.operations.get_portfolio(account_id=account.id)
                
                total_balance = 0.0
                
                # Суммируем стоимость всех позиций в портфеле
                for position in portfolio.positions:
                    market_value = position.current_price
                    if market_value:
                        position_value = (market_value.units + market_value.nano / 1e9) * position.quantity.units
                        total_balance += position_value

                # Добавляем баланс текущего счета к общей сумме по всем счетам
                total_all_accounts += total_balance
                print(f"Баланс счета {account.id}: {total_balance:.2f} RUB")
            
            # Вывод общей суммы по всем счетам
            print(f"Общая сумма по всем счетам: {total_all_accounts:.2f} RUB")
        
        except Exception as e:
            print(f"Произошла ошибка: {e}")

# Вызов функции
get_account_balance(TOKEN)
