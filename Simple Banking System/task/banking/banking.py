import random
import sqlite3


# Write your code here
# function below generate random number with length

class Account:

    @staticmethod
    def rand_num(length):
        return int(random.random() * 10 ** length)

    @staticmethod
    def luhn_card(card_number=None):
        if not card_number:
            card = list("400000" + str(Account.rand_num(9)).zfill(9))
        else:
            card = list(card_number)
            del card[-1]
        card_temp = list(map(int, card))
        for i in range(len(card_temp)):
            if i % 2 == 0:
                card_temp[i] *= 2
            if card_temp[i] > 9:
                card_temp[i] -= 9
        check_sum = (10 - sum(card_temp) % 10) if sum(card_temp) % 10 > 0 else 0
        return "".join(card) + str(check_sum)

    def __init__(self):
        self.card_number = Account.luhn_card()
        self.pin = str(Account.rand_num(4)).zfill(4)
        self.balance = 0

    def create_card(self):
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        with conn:
            cur.execute("INSERT INTO card(number, pin, balance) VALUES (:number, :pin, :balance)",
                        {'number': self.card_number, 'pin': self.pin, 'balance': self.balance})
        conn.close()

    @staticmethod
    def login(card_number, pin):
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM card where number = :number and pin = :pin",
                    {'number': card_number, 'pin': pin})
        login_status = cur.fetchone()
        conn.close()
        return True if login_status is not None else False

    @staticmethod
    def get_balance(card_number):
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        cur.execute("SELECT balance FROM card where number = :number",
                    {'number': card_number})
        balance = cur.fetchone()
        conn.close()
        return int(balance[0])

    @staticmethod
    def add_income(amount, card_number):
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        with conn:
            cur.execute("UPDATE card set balance = balance + :amount where number = :number",
                        {'amount': amount, 'number': card_number})
        conn.close()

    @staticmethod
    def make_transfer(card_number, target_number):
        # Check Luhn algorithm
        if Account.luhn_card(target_number) != target_number or card_number == target_number:
            print("Probably you made a mistake in the card number. Please try again!")
            return False
        # print("Pass luhn")
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        # Check existing in a database
        cur.execute("SELECT balance FROM card where number = :number",
                    {'number': target_number})
        if not cur.fetchone():
            print("Such a card does not exist.")
            conn.close()
            return False
        amount = int(input("Enter how much money you want to transfer:\n"))
        cur.execute("SELECT balance FROM card where number = :number",
                    {'number': card_number})
        balance = int(cur.fetchone()[0])
        if amount > balance:
            print("Not enough money!")
            return False
        if amount > 0:
            with conn:
                cur.execute("UPDATE card set balance = balance + :amount where number = :number",
                            {'amount': amount, 'number': target_number})
                cur.execute("UPDATE card set balance = balance - :amount where number = :number",
                            {'amount': amount, 'number': card_number})
        conn.close()
        return True

    @staticmethod
    def close_account(card_number):
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        with conn:
            cur.execute("Delete from card where number = :number",
                        {'number': card_number})
        conn.close()


def main():
    conn = sqlite3.connect('card.s3db')
    cur = conn.cursor()
    with conn:
        cur.execute("""create table IF NOT EXISTS card(
                    id INTEGER primary key autoincrement,
                    number TEXT,
                    pin TEXT,
                    balance INTEGER DEFAULT 0)""")
    conn.close()
    while True:
        print("1. Create an account")
        print("2. Log into account")
        print("0. Exit")
        choice = input()
        if choice == "1":
            account = Account()
            print("Your card has been created")
            print(f"Your card number:\n{account.card_number}")
            print(f"Your PIN:\n{account.pin}")
            account.create_card()
        if choice == "2":
            card_number = input("Enter your card number:\n")
            pin = input("Enter your PIN:\n")
            if Account.login(card_number, pin):
                print("You have successfully logged in!")
                while True:
                    print("1. Balance")
                    print("2. Add income")
                    print("3. Do transfer")
                    print("4. Close account")
                    print("5. Log out")
                    print("0. Exit")
                    choice = input()
                    if choice == "1":
                        print("Balance: " + str(Account.get_balance(card_number)))
                    elif choice == "2":
                        amount = int(input("Enter income:\n"))
                        Account.add_income(amount, card_number)
                        print("Income was added!")
                    elif choice == "3":
                        print("Transfer")
                        target_number = input("Enter card number:\n")
                        if Account.make_transfer(card_number, target_number):
                            print("Success!")
                    elif choice == "4":
                        Account.close_account(card_number)
                        print("The account has been closed!")
                        break
                    elif choice == "5":
                        print("You have successfully logged out!")
                        break
                    elif choice == "0":
                        print("Bye!")
                        exit()
            else:
                print("Wrong card number or PIN!")
        if choice == "0":
            print("Bye!")
            exit()


main()
