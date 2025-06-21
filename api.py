import asyncio
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Banking Transaction Data API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration models
class StreamConfig(BaseModel):
    frequency_seconds: float = 1.0
    fraud_injection_rate: float = 0.05  # 5% of transactions will be fraudulent patterns
    batch_size: int = 1

class Transaction(BaseModel):
    transaction_id: str
    account_id: str
    branch_id: int
    transaction_amount_vnd: float
    transaction_hour: int
    transaction_timestamp: str
    location_city: str
    device_id: str
    biometric_failure_count: int
    transaction_frequency_5min: int
    total_loans_vnd: float
    num_transactions: int
    npl_flag: bool
    total_deposits_vnd: float
    transaction_fees_vnd: float

# Global configuration
current_config = StreamConfig()
is_streaming = False

# Transaction generator
class TransactionDataGenerator:
    def __init__(self):
        self.cities = ["Ho Chi Minh City", "Hanoi", "Da Nang", "Can Tho", "Hai Phong", "Bien Hoa", "Hue", "Nha Trang"]
        self.transaction_counter = 1
        self.account_pool = [f"ACC_{i:06d}" for i in range(1000, 5000)]  # Pool of accounts
        self.device_pool = [f"DEV_{i:05d}" for i in range(10000, 50000)]  # Pool of devices
        self.recent_activity = {}  # Track recent activity per account
        
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
        
        # Update frequency tracking
        freq_5min = self._update_account_activity(account_id)
        
        # Normal transaction patterns
        return Transaction(
            transaction_id=f"TXN_{self.transaction_counter:08d}",
            account_id=account_id,
            branch_id=random.randint(1, 10),
            transaction_amount_vnd=max(10000, np.random.lognormal(mean=13.8, sigma=1.2)),  # Normal amounts
            transaction_hour=current_time.hour,
            transaction_timestamp=current_time.isoformat(),
            location_city=random.choice(self.cities),
            device_id=random.choice(self.device_pool),
            biometric_failure_count=random.choices([0, 1, 2], weights=[85, 12, 3])[0],  # Mostly successful
            transaction_frequency_5min=freq_5min,
            total_loans_vnd=max(0, np.random.lognormal(mean=13.0, sigma=1.5)),
            num_transactions=random.randint(50, 500),
            npl_flag=random.random() < 0.0198,  # 1.98% as per spec
            total_deposits_vnd=max(0, np.random.lognormal(mean=13.1, sigma=1.4)),
            transaction_fees_vnd=0  # Will be calculated
        )
    
    def _generate_money_laundering_transaction(self) -> Transaction:
        """Generate transaction with money laundering patterns"""
        account_id = random.choice(self.account_pool)
        current_time = datetime.now()
        
        # Simulate high frequency by adding multiple recent transactions
        for _ in range(random.randint(15, 25)):
            self.recent_activity.setdefault(account_id, []).append(time.time() - random.randint(1, 300))
        
        freq_5min = self._update_account_activity(account_id)
        
        return Transaction(
            transaction_id=f"TXN_{self.transaction_counter:08d}",
            account_id=account_id,
            branch_id=random.randint(1, 10),
            transaction_amount_vnd=random.uniform(300_000_000, 1_000_000_000),  # Large amounts
            transaction_hour=random.choice([1, 2, 3, 23, 24]),  # Off hours
            transaction_timestamp=current_time.isoformat(),
            location_city=random.choice(self.cities),
            device_id=random.choice(self.device_pool),
            biometric_failure_count=random.choices([0, 1], weights=[70, 30])[0],
            transaction_frequency_5min=freq_5min,  # Will be high due to simulation above
            total_loans_vnd=max(0, np.random.lognormal(mean=13.0, sigma=1.5)),
            num_transactions=random.randint(200, 800),  # Higher transaction history
            npl_flag=random.random() < 0.05,  # Slightly higher NPL rate
            total_deposits_vnd=max(0, np.random.lognormal(mean=14.0, sigma=1.2)),  # Higher deposits
            transaction_fees_vnd=0
        )
    
    def _generate_account_takeover_transaction(self) -> Transaction:
        """Generate transaction with account takeover patterns"""
        account_id = random.choice(self.account_pool)
        current_time = datetime.now()
        freq_5min = self._update_account_activity(account_id)
        
        # New device not in pool (simulating compromise)
        suspicious_device = f"DEV_NEW_{random.randint(90000, 99999)}"
        
        return Transaction(
            transaction_id=f"TXN_{self.transaction_counter:08d}",
            account_id=account_id,
            branch_id=random.randint(1, 10),
            transaction_amount_vnd=random.uniform(50_000_000, 500_000_000),  # Large but not extreme
            transaction_hour=random.choice([2, 3, 4, 22, 23]),  # Off hours
            transaction_timestamp=current_time.isoformat(),
            location_city=random.choice(["Unknown", "Foreign_Location"] + self.cities),  # New locations
            device_id=suspicious_device,  # New/suspicious device
            biometric_failure_count=random.randint(3, 5),  # Multiple failures
            transaction_frequency_5min=freq_5min,
            total_loans_vnd=max(0, np.random.lognormal(mean=13.0, sigma=1.5)),
            num_transactions=random.randint(100, 300),
            npl_flag=random.random() < 0.0198,
            total_deposits_vnd=max(0, np.random.lognormal(mean=13.5, sigma=1.3)),
            transaction_fees_vnd=0
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
            transaction_amount_vnd=random.uniform(100_000_000, 800_000_000),  # Large loan amounts
            transaction_hour=current_time.hour,
            transaction_timestamp=current_time.isoformat(),
            location_city=random.choice(self.cities),
            device_id=f"DEV_NEW_{random.randint(80000, 89999)}",  # New device for loan
            biometric_failure_count=random.choices([0, 1, 2], weights=[60, 25, 15])[0],
            transaction_frequency_5min=freq_5min,
            total_loans_vnd=random.uniform(500_000_000, 2_000_000_000),  # Very high loans
            num_transactions=random.randint(1, 50),  # Low transaction history (new account)
            npl_flag=random.random() < 0.15,  # Much higher NPL rate (15%)
            total_deposits_vnd=max(0, np.random.lognormal(mean=12.0, sigma=1.8)),  # Lower deposits
            transaction_fees_vnd=0
        )
    
    def _generate_fee_manipulation_transaction(self) -> Transaction:
        """Generate transaction with fee manipulation patterns"""
        account_id = random.choice(self.account_pool)
        current_time = datetime.now()
        
        # Simulate high frequency for fee manipulation
        for _ in range(random.randint(12, 20)):
            self.recent_activity.setdefault(account_id, []).append(time.time() - random.randint(1, 300))
        
        freq_5min = self._update_account_activity(account_id)
        
        # Small amounts but high frequency
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
            transaction_frequency_5min=freq_5min,  # Will be high
            total_loans_vnd=max(0, np.random.lognormal(mean=13.0, sigma=1.5)),
            num_transactions=random.randint(300, 1000),  # Very high transaction count
            npl_flag=random.random() < 0.0198,
            total_deposits_vnd=max(0, np.random.lognormal(mean=13.1, sigma=1.4)),
            transaction_fees_vnd=small_amount * 0.05  # Unusually high fee ratio
        )
    
    def generate_transaction(self) -> Transaction:
        """Generate a transaction (normal or fraudulent pattern)"""
        # Decide if this should be a fraudulent pattern
        if random.random() < current_config.fraud_injection_rate:
            # Choose fraud type
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
            else:  # fee_manipulation
                transaction = self._generate_fee_manipulation_transaction()
        else:
            transaction = self._generate_normal_transaction()
        
        # Calculate transaction fees (0.1% of deposits if not already set)
        if transaction.transaction_fees_vnd == 0:
            transaction.transaction_fees_vnd = transaction.total_deposits_vnd * 0.001
        
        self.transaction_counter += 1
        return transaction

# Global generator
generator = TransactionDataGenerator()

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "Banking Transaction Data API",
        "description": "Sends raw transaction data for fraud detection testing",
        "status": "active",
        "streaming": is_streaming,
        "config": current_config.model_dump()
    }

@app.post("/config")
async def update_config(config: StreamConfig):
    """Update streaming configuration"""
    global current_config
    current_config = config
    logger.info(f"Configuration updated: {config.model_dump()}")
    return {"message": "Configuration updated successfully", "config": config.model_dump()}

@app.get("/config")
async def get_config():
    """Get current configuration"""
    return current_config.model_dump()

@app.get("/transaction")
async def get_single_transaction():
    """Get a single transaction"""
    transaction = generator.generate_transaction()
    return transaction.model_dump()

@app.get("/transactions/{count}")
async def get_transactions_batch(count: int):
    """Get multiple transactions"""
    if count > 1000:
        raise HTTPException(status_code=400, detail="Maximum 1000 transactions per request")
    
    transactions = []
    for _ in range(count):
        transaction = generator.generate_transaction()
        transactions.append(transaction.model_dump())
    
    return {
        "transactions": transactions,
        "count": len(transactions),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/stream")
async def stream_transactions():
    """Continuously stream transaction data"""
    async def generate_stream():
        global is_streaming
        is_streaming = True
        
        try:
            while is_streaming:
                # Generate batch of transactions
                transactions = []
                for _ in range(current_config.batch_size):
                    transaction = generator.generate_transaction()
                    transactions.append(transaction.model_dump())
                
                # Send data packet
                data_packet = {
                    "timestamp": datetime.now().isoformat(),
                    "transactions": transactions
                }
                
                yield f"data: {json.dumps(data_packet)}\n\n"
                
                # Wait for next batch
                await asyncio.sleep(current_config.frequency_seconds)
                
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'error': str(e), 'timestamp': datetime.now().isoformat()})}\n\n"
        finally:
            is_streaming = False
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

@app.post("/start")
async def start_streaming():
    """Start transaction streaming"""
    global is_streaming
    if is_streaming:
        raise HTTPException(status_code=400, detail="Stream is already running")
    
    is_streaming = True
    logger.info("Transaction streaming started")
    return {"message": "Transaction streaming started", "config": current_config.model_dump()}

@app.post("/stop")
async def stop_streaming():
    """Stop transaction streaming"""
    global is_streaming
    is_streaming = False
    logger.info("Transaction streaming stopped")
    return {"message": "Transaction streaming stopped"}

@app.get("/status")
async def get_status():
    """Get API status"""
    return {
        "streaming": is_streaming,
        "transactions_generated": generator.transaction_counter - 1,
        "active_accounts": len(generator.recent_activity),
        "config": current_config.model_dump()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)