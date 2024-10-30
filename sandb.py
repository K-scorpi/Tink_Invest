# Description: Скрипт для создания аккаунта в песочнице Tinkoff Invest API.

# Импорт необходимых библиотек.
import logging
import os
from sec import sand_token
from decimal import Decimal

# Импорт классов и функций из библиотеки Tinkoff Invest API.
from tinkoff.invest import MoneyValue
from tinkoff.invest.sandbox.client import SandboxClient
from tinkoff.invest.utils import decimal_to_quotation, quotation_to_decimal

# Получение токена инвестиций из переменных окружения.
TOKEN = sand_token

# Баланс пополнения в рублях.
BALANCE = 5000000

# Конфигурация модуля logging для вывода логов с определенным уровнем.
logging.basicConfig(level=logging.DEBUG)
# Создание экземпляра logging с именем текущего модуля.
logger = logging.getLogger(__name__)


def main():
    # Создание клиента песочницы с использованием токена инвестиций.
    with SandboxClient(TOKEN) as client:
        # Преобразование десятичных чисел.
        balance = decimal_to_quotation(Decimal(BALANCE))

        # Получение всех счетов в песочнице.
        sandbox_accounts = client.users.get_accounts()

        # Закрытие всех счетов в песочнице.
        for sandbox_account in sandbox_accounts.accounts:
            client.sandbox.close_sandbox_account(account_id=sandbox_account.id)

        # Открытие нового счета в песочнице.
        sandbox_account = client.sandbox.open_sandbox_account()
        # Получение ID нового счета.
        account_id = sandbox_account.account_id

        # Добавление рублей на новый счет.
        client.sandbox.sandbox_pay_in(
            account_id=account_id,
            amount=MoneyValue(units=balance.units, nano=balance.nano, currency="rub")
        )

        # Вывод баланса счета.
        positions = client.operations.get_positions(account_id=account_id).money[0]
        logger.info(f"Баланс: {float(quotation_to_decimal(positions))} рублей.")


# Выполнение главной функции, если этот скрипт запущен напрямую.
if __name__ == "__main__":
    main()
