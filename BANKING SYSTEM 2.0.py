import csv
import re

class Banking_System:
    def __init__(self):
        self.accounts_file = "bank_accounts.csv"
        self.current_user = None
        self.MIN_BALANCE = 25000
        self.initialize_csv()

    def initialize_csv(self):
        #Create the header of the csv file if it does not exist yet
        try:
            with open(self.accounts_file, 'x', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=[
                    "AccountID", "Name", "Password", "Email", 
                    "Type", "Balance"
                ])
                writer.writeheader()
        except FileExistsError:
            pass

    def generate_account_id(self):
        #Create 3-digit account ID Number
        with open(self.accounts_file, 'r') as file:
            accounts = list(csv.DictReader(file))
            return f"{len(accounts) + 1:03d}"

    def validate_email(self, email):
        #Basic email validation
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    def validate_password(self, password):
        #Check 5-digit password
        return password.isdigit() and len(password) == 5

    def save_account(self, account_data):
        #Save new account to CSV
        with open(self.accounts_file, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=account_data.keys())
            writer.writerow(account_data)

    def find_account(self, name):
        #Look for other user account
        with open(self.accounts_file, 'r') as file:
            reader = csv.DictReader(file)
            for account in reader:
                if account["Name"].lower() == name.lower():
                    return account
        return None

    def update_account(self, updated_account):
        #Update the account

        # Read all accounts
        with open(self.accounts_file, 'r') as file:
            accounts = list(csv.DictReader(file))
        
        # Update the specific account
        for i, acc in enumerate(accounts):
            if acc["AccountID"] == updated_account["AccountID"]:
                accounts[i] = updated_account
                break
        
        # Write all accounts back
        with open(self.accounts_file, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=updated_account.keys())
            writer.writeheader()
            writer.writerows(accounts)

    def update_accounts(self, updated_accounts):
        """Save multiple account changes"""
        # Read all accounts
        with open(self.accounts_file, 'r') as file:
            accounts = list(csv.DictReader(file))
        
        # Update changed accounts
        for updated in updated_accounts:
            for i, acc in enumerate(accounts):
                if acc["AccountID"] == updated["AccountID"]:
                    accounts[i] = updated
                    break
        
        # Write back to file
        with open(self.accounts_file, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=updated_accounts[0].keys())
            writer.writeheader()
            writer.writerows(accounts)

    def create_account(self):
        #New account setup
        print("\n=== Create Your Account ===")
        
        # Get account type
        while True:
            print("\nAccount Types:")
            print("1. Savings (Withdrawal limit: FCFA 25,000)")
            print("2. Current (No limits)")
            choice = input("Choose Between (1/2): ")
            
            if choice == "1":
                account_type = "Savings"
                break
            elif choice == "2":
                account_type = "Current"
                break
            else:
                print("Invalid choice. Please Try again.")

        # Get user details
        while True:
            name = input("\nFull Name: ").strip()
            if name:
                break
            print("Name cannot be empty pardon !")

        while True:
            password = input("Create 5-digit password: ")
            if self.validate_password(password):
                break
            print("Password must be 5 numbers!")

        while True:
            email = input("Email: ").strip()
            if self.validate_email(email):
                break
            print("Invalid email format! it should contain @ and .com")

        # Create account
        account_id = self.generate_account_id()
        new_account = {
            "AccountID": account_id,
            "Name": name,
            "Password": password,
            "Email": email,
            "Type": account_type,
            "Balance": str(self.MIN_BALANCE)
        }

        self.save_account(new_account)
        print(f"\nYour Account hase been created Successfully Your ID is: {account_id}")
        print(f"This is your Initial balance: {self.MIN_BALANCE:,} FCFA")
        return new_account

    def login(self):
        """User login"""
        print("\n=== Login ===")
        name = input("Enter Your Name: ").strip()
        password = input("Enter your Password: ").strip()
        
        account = self.find_account(name)
        if account and account["Password"] == password:
            print(f"\nWelcome back, {account['Name']}!")
            return account
        else:
            print("\nLogin failed. Please Check either your name or password.")
            return None

    def deposit(self, account):
        #Add money to account
        while True:
            try:
                amount = float(input("\nDeposit The amount: "))
                if amount > 0:
                    break
                print("Amount must be positive!")
            except ValueError:
                print("Invalid number!")

        current_balance = float(account["Balance"])
        account["Balance"] = str(current_balance + amount)
        self.update_account(account)  # Save the change
        print(f"\nNew balance: {float(account['Balance']):,.2f} FCFA")

    def withdraw(self, account):
        #Remove money with checks
        current_balance = float(account["Balance"])
        
        if current_balance == self.MIN_BALANCE:
            print("\nYou Cannot withdraw - minimum balance reached!")
            return

        print(f"\nYou are capable to withdraw: {current_balance - self.MIN_BALANCE:,.2f} FCFA")
        
        while True:
            try:
                amount = float(input("Withdraw amount: "))
                if amount <= 0:
                    print("Amount must be positive!")
                elif account["Type"] == "Savings" and amount > 25000:
                    print("Savings accounts cannot withdraw > 25,000 FCFA")
                elif (current_balance - amount) < self.MIN_BALANCE:
                    print(f"Cannot go below minimum {self.MIN_BALANCE:,} FCFA")
                else:
                    account["Balance"] = str(current_balance - amount)
                    self.update_account(account)  # Save the change
                    print(f"\nWithdrew {amount:,.2f} FCFA")
                    print(f"New balance: {float(account['Balance']):,.2f} FCFA")
                    return
            except ValueError:
                print("Invalid number!")

    def transfer(self, sender):
        #Send money to another account
        current_balance = float(sender["Balance"])
        
        if current_balance == self.MIN_BALANCE:
            print("\nYou Cannot transfer again - minimum balance reached!")
            return

        print(f"\nYou are capable to transfer: {current_balance - self.MIN_BALANCE:,.2f} FCFA")
        recipient_name = input("\nReceivers name: ").strip()
        recipient = self.find_account(recipient_name)
        
        if not recipient:
            print("Account not found!")
            return
        if sender["AccountID"] == recipient["AccountID"]:
            print("You Cannot transfer Money to yourself!")
            return

        while True:
            try:
                amount = float(input("Transfer amount: "))
                if amount <= 0:
                    print("Amount must be positive!")
                elif sender["Type"] == "Savings" and amount > 25000:
                    print("Savings accounts cannot transfer > 25,000 FCFA")
                elif (current_balance - amount) < self.MIN_BALANCE:
                    print(f"Cannot go below minimum {self.MIN_BALANCE:,} FCFA")
                else:
                    # Update both accounts
                    sender["Balance"] = str(current_balance - amount)
                    recipient["Balance"] = str(float(recipient["Balance"]) + amount)
                    
                    # Save changes
                    self.update_accounts([sender, recipient])
                    print(f"\nSuccessful Transfer of {amount:,.2f} FCFA to {recipient['Name']}")
                    print(f"Your new balance is: {float(sender['Balance']):,.2f} FCFA")
                    return
            except ValueError:
                print("Invalid number!")

    def check_balance(self, account):
        """Display current balance"""
        balance = float(account["Balance"])
        print(f"\nYour Current balance is: {balance:,.2f} FCFA")
        if balance == self.MIN_BALANCE:
            print("You have reached the minimum balance limit")

    def main_menu(self):
        #Main program visual aspect
        while True:
            print("\n=== Welcome to MAEVA Banking System ===")
            print("\n=== MAIN MENU ===")
            print("1. Create Account")
            print("2. Login")
            print("3. Exit")
            
            choice = input("Choose (1-3): ")
            
            if choice == "1":
                account = self.create_account()
                if account:
                    self.transaction_menu(account)
            elif choice == "2":
                account = self.login()
                if account:
                    self.transaction_menu(account)
            elif choice == "3":
                print("\nThank you for Using De-Kini Banking System see you soon!")
                break
            else:
                print("Invalid choice. Please Try again.")

    def transaction_menu(self, account):
        """Banking operations menu"""
        while True:
            print("\n=== Our Various Transactions ===")
            print("1. Deposit")
            print("2. Withdraw")
            print("3. Check Balance")
            print("4. Transfer")
            print("5. Logout")
            
            choice = input("Choose (1-5): ")
            
            if choice == "1":
                self.deposit(account)
            elif choice == "2":
                self.withdraw(account)
            elif choice == "3":
                self.check_balance(account)
            elif choice == "4":
                self.transfer(account)
            elif choice == "5":
                print("\nLogged out successfully.")
                break
            else:
                print("Invalid choice. Try again.")

def run_program():
    """Starter function that begins the banking system"""
    print("=== WELCOME TO MAEVA Banking System ===")
    bank = Banking_System()
    bank.main_menu()

# Start the program
run_program()