import asyncio
from tinkoff.invest import AsyncClient
from sec import token
from tabulate import tabulate  # Импортируем tabulate
from colorama import Fore, Style  # Импортируем colorama

TOKEN = token

class AccountManager:
    def __init__(self, token: str):
        self.token = token
        self.total_balance = 0.0

    async def get_accounts(self):
        """Получение списка счетов асинхронно."""
        async with AsyncClient(self.token) as client:
            accounts = await client.users.get_accounts()
            return accounts.accounts

    async def get_portfolio(self, account_id):
        """Получение портфеля для конкретного счета асинхронно."""
        async with AsyncClient(self.token) as client:
            portfolio = await client.operations.get_portfolio(account_id=account_id)
            return portfolio

    async def calculate_balance(self, portfolio):
        """Подсчет общего баланса по портфелю асинхронно."""
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

    async def print_portfolio_changes(self, portfolio):
        """Вывод изменений цен бумаг в виде таблицы асинхронно."""
        headers = ['Название актива', 'Стоимость покупки', 'Текущая стоимость', 'Разница']
        table = []

        for position in portfolio.positions:
            figi = position.figi
            quantity = position.quantity.units
            current_price = position.current_price
            average_position_price = position.average_position_price  # Средняя цена покупки

            if current_price and quantity > 0:
                market_value = current_price.units + current_price.nano / 1e9
                price_difference = market_value - (average_position_price.units + average_position_price.nano / 1e9)

                # Устанавливаем цвет в зависимости от разницы
                if price_difference > 0:
                    color = Fore.GREEN
                elif price_difference < 0:
                    color = Fore.RED
                else:
                    color = Fore.YELLOW  # Для нейтрального значения

                # Добавляем данные в таблицу с цветами
                table.append([
                    f"{figi}{Style.RESET_ALL}",  # Сброс цвета после использования
                    f"{average_position_price.units + average_position_price.nano / 1e9:.2f}",
                    f"{market_value:.2f}",
                    f"{color}{price_difference:.2f}{Style.RESET_ALL}"  # Цвет для разницы
                ])
            else:
                print(f"Нет текущей цены для актива {figi}.")

        # Вывод таблицы
        print("\nИзменения цен бумаг:")
        print(tabulate(table, headers, tablefmt="grid"))  # Используем tabulate для форматирования

    async def display_account_balances(self):
        """Отображение балансов всех счетов и изменений цен активов асинхронно."""
        accounts = await self.get_accounts()
        
        if not accounts:
            print("Счета не найдены.")
            return
        
        for account in accounts:
            print(f"\nСчет: {account.id}, тип: {account.type}")
            portfolio = await self.get_portfolio(account.id)
            total_balance = await self.calculate_balance(portfolio)
            self.total_balance += total_balance
            
            print(f"Баланс счета {account.id}: {total_balance:.2f} RUB")
            await self.print_portfolio_changes(portfolio)

        print(f"\nОбщая сумма по всем счетам: {self.total_balance:.2f} RUB")

# Запуск асинхронной функции
async def main():
    account_manager = AccountManager(TOKEN)
    await account_manager.display_account_balances()

# Запуск программы
if __name__ == "__main__":
    asyncio.run(main())
