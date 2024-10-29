from tinkoff.invest import Client
from sec import token

TOKEN = token

class AccountManager:
    def __init__(self, token: str):
        self.token = token
        self.total_balance = 0.0

    def get_accounts(self):
        """Получение списка счетов."""
        with Client(self.token) as client:
            accounts = client.users.get_accounts().accounts
            return accounts

    def get_portfolio(self, account_id):
        """Получение портфеля для конкретного счета."""
        with Client(self.token) as client:
            portfolio = client.operations.get_portfolio(account_id=account_id)
            return portfolio

    def calculate_balance(self, portfolio):
        """Подсчет общего баланса по портфелю."""
        total_balance = 0.0
        if not portfolio.positions:
            return total_balance
        
        for position in portfolio.positions:
            current_price = position.current_price
            quantity = position.quantity.units
            
            if current_price:
                market_value = current_price.units + current_price.nano / 1e9
                position_value = market_value * quantity
                total_balance += position_value
        
        return total_balance

    def print_portfolio_changes(self, portfolio):
        """Вывод изменений цен бумаг в виде таблицы."""
        print("\nИзменения цен бумаг:")
        print(f"{'Название актива':<25} {'Стоимость покупки':<20} {'Текущая стоимость':<20} {'Разница':<15}")
        print("-" * 80)

        for position in portfolio.positions:
            figi = position.figi
            quantity = position.quantity.units
            current_price = position.current_price
            average_position_price = position.average_position_price  # Средняя цена покупки

            if current_price and quantity > 0:
                market_value = current_price.units + current_price.nano / 1e9
                price_difference = market_value - (average_position_price.units + average_position_price.nano / 1e9)

                print(f"{figi:<25} {average_position_price.units + average_position_price.nano / 1e9:<20.2f} "
                      f"{market_value:<20.2f} {price_difference:<15.2f}")
            else:
                print(f"Нет текущей цены для актива {figi}.")

    def display_account_balances(self):
        """Отображение балансов всех счетов и изменений цен активов."""
        accounts = self.get_accounts()
        
        if not accounts:
            print("Счета не найдены.")
            return
        
        for account in accounts:
            print(f"\nСчет: {account.id}, тип: {account.type}")
            portfolio = self.get_portfolio(account.id)
            total_balance = self.calculate_balance(portfolio)
            self.total_balance += total_balance
            
            print(f"Баланс счета {account.id}: {total_balance:.2f} RUB")
            self.print_portfolio_changes(portfolio)

        print(f"\nОбщая сумма по всем счетам: {self.total_balance:.2f} RUB")


# Создание экземпляра AccountManager и вывод балансов
account_manager = AccountManager(TOKEN)
account_manager.display_account_balances()
