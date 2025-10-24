from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import datetime
import random
from enum import Enum
from dataclasses import dataclass
import os

# ===== BANKING SYSTEM CLASSES =====
class AccountType(Enum):
    SAVINGS = "savings"
    CHECKING = "checking"
    BUSINESS = "business"
    STUDENT = "student"

class TransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    INTEREST = "interest"

@dataclass
class Address:
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"
    
    def to_dict(self):
        return {
            'street': self.street,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'country': self.country
        }

class Person:
    def __init__(self, first_name, last_name, email, phone, address, date_of_birth):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.address = address
        self.date_of_birth = date_of_birth
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address.to_dict(),
            'date_of_birth': self.date_of_birth
        }

class Transaction:
    def __init__(self, transaction_id, account_number, transaction_type, amount, description=""):
        self.transaction_id = transaction_id
        self.account_number = account_number
        self.transaction_type = transaction_type
        self.amount = amount
        self.description = description
        self.timestamp = datetime.datetime.now()
        self.status = "completed"
    
    def to_dict(self):
        return {
            'transaction_id': self.transaction_id,
            'account_number': self.account_number,
            'transaction_type': self.transaction_type.value,
            'amount': self.amount,
            'description': self.description,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status
        }

class BankAccount:
    def __init__(self, account_number, account_holder, account_type, initial_balance=0.0):
        self.account_number = account_number
        self.account_holder = account_holder
        self.account_type = account_type
        self.balance = initial_balance
        self.interest_rate = self._get_interest_rate()
        self.is_active = True
        self.date_opened = datetime.datetime.now()
        self.transactions = []
    
    def _get_interest_rate(self):
        rates = {
            AccountType.SAVINGS: 0.02,
            AccountType.CHECKING: 0.001,
            AccountType.BUSINESS: 0.015,
            AccountType.STUDENT: 0.025
        }
        return rates.get(self.account_type, 0.01)
    
    def deposit(self, amount, description=""):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        if not self.is_active:
            raise ValueError("Account is not active")
        
        self.balance += amount
        transaction = Transaction(
            transaction_id=self._generate_transaction_id(),
            account_number=self.account_number,
            transaction_type=TransactionType.DEPOSIT,
            amount=amount,
            description=description
        )
        self.transactions.append(transaction)
        return True
    
    def withdraw(self, amount, description=""):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        if not self.is_active:
            raise ValueError("Account is not active")
        
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        
        self.balance -= amount
        transaction = Transaction(
            transaction_id=self._generate_transaction_id(),
            account_number=self.account_number,
            transaction_type=TransactionType.WITHDRAWAL,
            amount=amount,
            description=description
        )
        self.transactions.append(transaction)
        return True
    
    def transfer(self, amount, target_account, description=""):
        if self.withdraw(amount, f"Transfer to {target_account.account_number}"):
            target_account.deposit(amount, f"Transfer from {self.account_number}")
            return True
        return False
    
    def get_transaction_history(self, days=30):
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        return [t for t in self.transactions if t.timestamp >= cutoff_date]
    
    def get_balance(self):
        return self.balance
    
    def _generate_transaction_id(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        random_num = random.randint(1000, 9999)
        return f"TXN{timestamp}{random_num}"
    
    def to_dict(self):
        return {
            'account_number': self.account_number,
            'account_holder': self.account_holder.to_dict(),
            'account_type': self.account_type.value,
            'balance': self.balance,
            'interest_rate': self.interest_rate,
            'is_active': self.is_active,
            'date_opened': self.date_opened.isoformat(),
            'transactions': [t.to_dict() for t in self.transactions]
        }

class Bank:
    def __init__(self, name, routing_number):
        self.name = name
        self.routing_number = routing_number
        self.accounts = {}
        self.customers = {}
    
    def create_account(self, account_holder, account_type, initial_deposit=0.0):
        if initial_deposit < 0:
            raise ValueError("Initial deposit cannot be negative")
        
        account_number = self._generate_account_number()
        account = BankAccount(account_number, account_holder, account_type, initial_deposit)
        
        self.accounts[account_number] = account
        self.customers[account_holder.email] = account_holder
        
        return account
    
    def get_account(self, account_number):
        return self.accounts.get(account_number)
    
    def transfer_between_accounts(self, from_account, to_account, amount, description=""):
        if from_account not in self.accounts:
            raise ValueError("Source account not found")
        
        if to_account not in self.accounts:
            raise ValueError("Destination account not found")
        
        source = self.accounts[from_account]
        destination = self.accounts[to_account]
        
        return source.transfer(amount, destination, description)
    
    def _generate_account_number(self):
        while True:
            account_number = f"{random.randint(10000000, 99999999)}"
            if account_number not in self.accounts:
                return account_number

# ===== FLASK APP =====
app = Flask(__name__)
# FIXED CORS CONFIGURATION FOR MOBILE
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize bank
bank = Bank("Digital Bank", "123456789")

# SERVE FRONTEND
@app.route('/')
def serve_frontend():
    try:
        return send_file('simple_frontend.html')
    except Exception as e:
        return jsonify({"error": f"Frontend file not found: {str(e)}"}), 404

# KEEP ALL YOUR EXISTING ROUTES AS THEY ARE
@app.route('/api/accounts', methods=['POST'])
def create_account():
    try:
        data = request.json
        print("Received data:", data)
        
        address = Address(
            street=data['address']['street'],
            city=data['address']['city'],
            state=data['address']['state'],
            zip_code=data['address']['zip_code']
        )
        
        person = Person(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data['phone'],
            address=address,
            date_of_birth=data['date_of_birth']
        )
        
        account_type = AccountType(data['account_type'])
        account = bank.create_account(person, account_type, float(data['initial_deposit']))
        
        return jsonify({
            "success": True,
            "account_number": account.account_number,
            "message": "Account created successfully"
        })
    
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/accounts/<account_number>', methods=['GET'])
def get_account(account_number):
    try:
        account = bank.get_account(account_number)
        if not account:
            return jsonify({"success": False, "error": "Account not found"}), 404
        
        return jsonify({
            "success": True,
            "account": account.to_dict()
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/accounts/<account_number>/deposit', methods=['POST'])
def deposit(account_number):
    try:
        data = request.json
        account = bank.get_account(account_number)
        
        if not account:
            return jsonify({"success": False, "error": "Account not found"}), 404
        
        account.deposit(float(data['amount']), data.get('description', ''))
        
        return jsonify({
            "success": True,
            "new_balance": account.get_balance(),
            "message": "Deposit successful"
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/accounts/<account_number>/withdraw', methods=['POST'])
def withdraw(account_number):
    try:
        data = request.json
        account = bank.get_account(account_number)
        
        if not account:
            return jsonify({"success": False, "error": "Account not found"}), 404
        
        account.withdraw(float(data['amount']), data.get('description', ''))
        
        return jsonify({
            "success": True,
            "new_balance": account.get_balance(),
            "message": "Withdrawal successful"
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/accounts/<from_account>/transfer', methods=['POST'])
def transfer(from_account):
    try:
        data = request.json
        to_account = data['to_account']
        amount = float(data['amount'])
        
        success = bank.transfer_between_accounts(
            from_account,
            to_account,
            amount,
            data.get('description', '')
        )
        
        if success:
            return jsonify({
                "success": True,
                "message": "Transfer successful"
            })
        else:
            return jsonify({"success": False, "error": "Transfer failed"}), 400
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/accounts/<account_number>/transactions', methods=['GET'])
def get_transactions(account_number):
    try:
        account = bank.get_account(account_number)
        if not account:
            return jsonify({"success": False, "error": "Account not found"}), 404
        
        days = request.args.get('days', 30, type=int)
        transactions = account.get_transaction_history(days)
        
        return jsonify({
            "success": True,
            "transactions": [t.to_dict() for t in transactions]
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "bank_name": bank.name,
        "total_accounts": len(bank.accounts),
        "total_customers": len(bank.customers)
    })

# ADD CORS HEADERS FOR MOBILE ACCESS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# UPDATE THE PORT CONFIGURATION AT THE BOTTOM
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)