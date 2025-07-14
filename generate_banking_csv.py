import csv
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np

class Transaction:
    def __init__(self, transaction_id, account_id, branch_id, transaction_amount_vnd,
                 transaction_hour, transaction_timestamp, location_city, device_id,
                 biometric_failure_count, transaction_frequency_5min, total_loans_vnd,
                 num_transactions, npl_flag, total_deposits_vnd, transaction_fees_vnd,
                 is_fraud=False, fraud_type=None):
        self.transaction_id = transaction_id
        self.account_id = account_id
        self.branch_id = branch_id
        self.transaction_amount_vnd = transaction_amount_vnd
        self.transaction_hour = transaction_hour
        self.transaction_timestamp = transaction_timestamp
        self.location_city = location_city
        self.device_id = device_id
        self.biometric_failure_count = biometric_failure_count
        self.transaction_frequency_5min = transaction_frequency_5min
        self.total_loans_vnd = total_loans_vnd
        self.num_transactions = num_transactions
        self.npl_flag = npl_flag
        self.total_deposits_vnd = total_deposits_vnd
        self.transaction_fees_vnd = transaction_fees_vnd
        self.is_fraud = is_fraud
        self.fraud_type = fraud_type
    
    def to_dict(self):
        return {
            'transaction_id': self.transaction_id,
            'account_id': self.account_id,
            'branch_id': self.branch_id,
            'transaction_amount_vnd': self.transaction_amount_vnd,
            'transaction_hour': self.transaction_hour,
            'transaction_timestamp': self.transaction_timestamp,
            'location_city': self.location_city,
            'device_id': self.device_id,
            'biometric_failure_count': self.biometric_failure_count,
            'transaction_frequency_5min': self.transaction_frequency_5min,
            'total_loans_vnd': self.total_loans_vnd,
            'num_transactions': self.num_transactions,
            'npl_flag': self.npl_flag,
            'total_deposits_vnd': self.total_deposits_vnd,
            'transaction_fees_vnd': self.transaction_fees_vnd,
            'is_fraud': self.is_fraud,
            'fraud_type': self.fraud_type if self.fraud_type else 'normal'
        }

class TransactionDataGenerator:
    def __init__(self):
        self.cities = ["Ho Chi Minh City", "Hanoi", "Da Nang", "Can Tho", "Hai Phong", "Bien Hoa", "Hue", "Nha Trang"]
        self.transaction_counter = 1
        self.account_pool = [f"ACC_{i:06d}" for i in range(1000, 5000)]
        self.device_pool = [f"DEV_{i:05d}" for i in range(10000, 50000)]
        self.recent_activity = {}
        self.fraud_injection_rate = 0.05  # 5% fraudulent transactions
        
    def _update_account_activity(self, account_id: str) -> int:
        """Track transaction frequency for accounts"""
        current_time = time.time()
        window_start = current_time - 300  # 5 minutes ago
        
        if account_id not in self.recent_activity:
            self.recent_activity[account_id] = []
        
        # Remove old transactions
        self.recent_activity[account_id] = [
            t for t in self.recent_activity[account_id] if t > window_start
        ]
        
        # Add current transaction
        self.recent_activity[account_id].append(current_time)
        
        return len(self.recent_activity[account_id])
    
    def _generate_normal_transaction(self) -> Transaction:
        """Generate a normal banking transaction"""
        account_id = random.choice(self.account_pool)
        current_time = datetime.now()
        
        freq_5min = self._update_account_activity(account_id)
        
        return Transaction(
            transaction_id=f"TXN_{self.transaction_counter:08d}",
            account_id=account_id,
            branch_id=random.randint(1, 10),
            transaction_amount_vnd=max(10000, np.random.lognormal(mean=13.8, sigma=1.2)),
            transaction_hour=current_time.hour,
            transaction_timestamp=current_time.isoformat(),
            location_city=random.choice(self.cities),
            device_id=random.choice(self.device_pool),
            biometric_failure_count=random.choices([0, 1, 2], weights=[85, 12, 3])[0],
            transaction_frequency_5min=freq_5min,
            total_loans_vnd=max(0, np.random.lognormal(mean=13.0, sigma=1.5)),
            num_transactions=random.randint(50, 500),
            npl_flag=random.random() < 0.0198,
            total_deposits_vnd=max(0, np.random.lognormal(mean=13.1, sigma=1.4)),
            transaction_fees_vnd=0,
            is_fraud=False,
            fraud_type=None
        )
    
    def _generate_money_laundering_transaction(self) -> Transaction:
        """Generate transaction with money laundering patterns"""
        account_id = random.choice(self.account_pool)
        current_time = datetime.now()
        
        # Simulate high frequency
        for _ in range(random.randint(15, 25)):
            self.recent_activity.setdefault(account_id, []).append(time.time() - random.randint(1, 300))
        
        freq_5min = self._update_account_activity(account_id)
        
        return Transaction(
            transaction_id=f"TXN_{self.transaction_counter:08d}",
            account_id=account_id,
            branch_id=random.randint(1, 10),
            transaction_amount_vnd=random.uniform(300_000_000, 1_000_000_000),
            transaction_hour=random.choice([1, 2, 3, 23, 24]),
            transaction_timestamp=current_time.isoformat(),
            location_city=random.choice(self.cities),
            device_id=random.choice(self.device_pool),
            biometric_failure_count=random.choices([0, 1], weights=[70, 30])[0],
            transaction_frequency_5min=freq_5min,
            total_loans_vnd=max(0, np.random.lognormal(mean=13.0, sigma=1.5)),
            num_transactions=random.randint(200, 800),
            npl_flag=random.random() < 0.05,
            total_deposits_vnd=max(0, np.random.lognormal(mean=14.0, sigma=1.2)),
            transaction_fees_vnd=0,
            is_fraud=True,
            fraud_type='money_laundering'
        )
    
    def _generate_account_takeover_transaction(self) -> Transaction:
        """Generate transaction with account takeover patterns"""
        account_id = random.choice(self.account_pool)
        current_time = datetime.now()
        freq_5min = self._update_account_activity(account_id)
        
        suspicious_device = f"DEV_NEW_{random.randint(90000, 99999)}"
        
        return Transaction(
            transaction_id=f"TXN_{self.transaction_counter:08d}",
            account_id=account_id,
            branch_id=random.randint(1, 10),
            transaction_amount_vnd=random.uniform(50_000_000, 500_000_000),
            transaction_hour=random.choice([2, 3, 4, 22, 23]),
            transaction_timestamp=current_time.isoformat(),
            location_city=random.choice(["Unknown", "Foreign_Location"] + self.cities),
            device_id=suspicious_device,
            biometric_failure_count=random.randint(3, 5),
            transaction_frequency_5min=freq_5min,
            total_loans_vnd=max(0, np.random.lognormal(mean=13.0, sigma=1.5)),
            num_transactions=random.randint(100, 300),
            npl_flag=random.random() < 0.0198,
            total_deposits_vnd=max(0, np.random.lognormal(mean=13.5, sigma=1.3)),
            transaction_fees_vnd=0,
            is_fraud=True,
            fraud_type='account_takeover'
        )
    
    def _generate_loan_fraud_transaction(self) -> Transaction:
        """Generate transaction with loan fraud patterns"""
        account_id = random.choice(self.account_pool)
        current_time = datetime.now()
        freq_5min = self._update_account_activity(account_id)
        
        return Transaction(
            transaction_id=f"TXN_{self.transaction_counter:08d}",
            account_id=account_id,
            branch_id=random.randint(1, 10),
            transaction_amount_vnd=random.uniform(100_000_000, 800_000_000),
            transaction_hour=current_time.hour,
            transaction_timestamp=current_time.isoformat(),
            location_city=random.choice(self.cities),
            device_id=f"DEV_NEW_{random.randint(80000, 89999)}",
            biometric_failure_count=random.choices([0, 1, 2], weights=[60, 25, 15])[0],
            transaction_frequency_5min=freq_5min,
            total_loans_vnd=random.uniform(500_000_000, 2_000_000_000),
            num_transactions=random.randint(1, 50),
            npl_flag=random.random() < 0.15,
            total_deposits_vnd=max(0, np.random.lognormal(mean=12.0, sigma=1.8)),
            transaction_fees_vnd=0,
            is_fraud=True,
            fraud_type='loan_fraud'
        )
    
    def _generate_fee_manipulation_transaction(self) -> Transaction:
        """Generate transaction with fee manipulation patterns"""
        account_id = random.choice(self.account_pool)
        current_time = datetime.now()
        
        # Simulate high frequency for fee manipulation
        for _ in range(random.randint(12, 20)):
            self.recent_activity.setdefault(account_id, []).append(time.time() - random.randint(1, 300))
        
        freq_5min = self._update_account_activity(account_id)
        small_amount = random.uniform(10_000, 100_000)
        
        return Transaction(
            transaction_id=f"TXN_{self.transaction_counter:08d}",
            account_id=account_id,
            branch_id=random.randint(1, 10),
            transaction_amount_vnd=small_amount,
            transaction_hour=current_time.hour,
            transaction_timestamp=current_time.isoformat(),
            location_city=random.choice(self.cities),
            device_id=random.choice(self.device_pool),
            biometric_failure_count=random.choices([0, 1], weights=[90, 10])[0],
            transaction_frequency_5min=freq_5min,
            total_loans_vnd=max(0, np.random.lognormal(mean=13.0, sigma=1.5)),
            num_transactions=random.randint(300, 1000),
            npl_flag=random.random() < 0.0198,
            total_deposits_vnd=max(0, np.random.lognormal(mean=13.1, sigma=1.4)),
            transaction_fees_vnd=small_amount * 0.05,
            is_fraud=True,
            fraud_type='fee_manipulation'
        )
    
    def generate_transaction(self) -> Transaction:
        """Generate a transaction (normal or fraudulent pattern)"""
        # Decide if this should be a fraudulent pattern
        if random.random() < self.fraud_injection_rate:
            fraud_type = random.choices(
                ['money_laundering', 'account_takeover', 'loan_fraud', 'fee_manipulation'],
                weights=[30, 25, 25, 20]
            )[0]
            
            if fraud_type == 'money_laundering':
                transaction = self._generate_money_laundering_transaction()
            elif fraud_type == 'account_takeover':
                transaction = self._generate_account_takeover_transaction()
            elif fraud_type == 'loan_fraud':
                transaction = self._generate_loan_fraud_transaction()
            else:
                transaction = self._generate_fee_manipulation_transaction()
        else:
            transaction = self._generate_normal_transaction()
        
        # Calculate transaction fees if not already set
        if transaction.transaction_fees_vnd == 0:
            transaction.transaction_fees_vnd = transaction.total_deposits_vnd * 0.001
        
        self.transaction_counter += 1
        return transaction

def generate_csv_file(num_transactions: int = 1000, filename: str = "banking_transactions.csv"):
    """Generate CSV file with banking transaction data"""
    generator = TransactionDataGenerator()
    
    # CSV headers
    fieldnames = [
        'transaction_id', 'account_id', 'branch_id', 'transaction_amount_vnd',
        'transaction_hour', 'transaction_timestamp', 'location_city', 'device_id',
        'biometric_failure_count', 'transaction_frequency_5min', 'total_loans_vnd',
        'num_transactions', 'npl_flag', 'total_deposits_vnd', 'transaction_fees_vnd',
        'is_fraud', 'fraud_type'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header
        writer.writeheader()
        
        # Generate and write transactions
        print(f"Generating {num_transactions} transactions...")
        for i in range(num_transactions):
            transaction = generator.generate_transaction()
            writer.writerow(transaction.to_dict())
            
            # Progress indicator
            if (i + 1) % 100 == 0:
                print(f"Generated {i + 1}/{num_transactions} transactions")
    
    print(f"CSV file '{filename}' created successfully with {num_transactions} transactions!")
    
    # Print summary statistics
    fraud_count = int(num_transactions * generator.fraud_injection_rate)
    print(f"\nSummary:")
    print(f"- Total transactions: {num_transactions}")
    print(f"- Expected fraudulent transactions: ~{fraud_count} ({generator.fraud_injection_rate*100}%)")
    print(f"- Normal transactions: ~{num_transactions - fraud_count}")

if __name__ == "__main__":
    # Generate CSV with 1000 transactions by default
    # You can change these parameters as needed
    generate_csv_file(
        num_transactions=1000,  # Change this to generate more/fewer transactions
        filename="banking_transactions.csv"  # Change filename if needed
    )