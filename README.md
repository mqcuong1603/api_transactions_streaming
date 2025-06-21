# Banking Transaction Data API

A FastAPI-based service that generates realistic banking transaction data for fraud detection testing and machine learning training. The API simulates various transaction patterns including normal banking activities and multiple fraud types.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone or download the project**
```bash
cd d:\Projects\api_transactions_streaming
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the API**
```bash
python api.py
```

The API will start on `http://localhost:8000`

### Verify Installation
Open your browser and navigate to:
- **API Home**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📖 API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication
No authentication required - this is a development/testing API.

## 🔧 Endpoints

### 1. Health Check
**GET /** - Get API information and status

```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "message": "Banking Transaction Data API",
  "description": "Sends raw transaction data for fraud detection testing",
  "status": "active",
  "streaming": false,
  "config": {
    "frequency_seconds": 1.0,
    "fraud_injection_rate": 0.05,
    "batch_size": 1
  }
}
```

### 2. Single Transaction
**GET /transaction** - Get a single randomly generated transaction

```bash
curl http://localhost:8000/transaction
```

**Response:**
```json
{
  "transaction_id": "TXN_00000001",
  "account_id": "ACC_001234",
  "branch_id": 5,
  "transaction_amount_vnd": 2500000.50,
  "transaction_hour": 14,
  "transaction_timestamp": "2024-12-19T14:30:45.123456",
  "location_city": "Ho Chi Minh City",
  "device_id": "DEV_12345",
  "biometric_failure_count": 0,
  "transaction_frequency_5min": 1,
  "total_loans_vnd": 50000000.00,
  "num_transactions": 145,
  "npl_flag": false,
  "total_deposits_vnd": 75000000.00,
  "transaction_fees_vnd": 75000.00
}
```

### 3. Batch Transactions
**GET /transactions/{count}** - Get multiple transactions (max 1000)

```bash
curl http://localhost:8000/transactions/10
```

**Response:**
```json
{
  "transactions": [
    {
      "transaction_id": "TXN_00000001",
      "account_id": "ACC_001234",
      ...
    },
    ...
  ],
  "count": 10,
  "timestamp": "2024-12-19T14:30:45.123456"
}
```

### 4. Real-time Streaming
**GET /stream** - Continuously stream transaction data (Server-Sent Events)

```bash
curl -N http://localhost:8000/stream
```

**Stream Format:**
```
data: {"timestamp": "2024-12-19T14:30:45.123456", "transactions": [...]}

data: {"timestamp": "2024-12-19T14:30:46.123456", "transactions": [...]}
```

### 5. Streaming Controls

#### Start Streaming
**POST /start** - Start the streaming service

```bash
curl -X POST http://localhost:8000/start
```

#### Stop Streaming
**POST /stop** - Stop the streaming service

```bash
curl -X POST http://localhost:8000/stop
```

### 6. Configuration Management

#### Get Configuration
**GET /config** - Get current streaming configuration

```bash
curl http://localhost:8000/config
```

#### Update Configuration
**POST /config** - Update streaming settings

```bash
curl -X POST http://localhost:8000/config \
  -H "Content-Type: application/json" \
  -d '{
    "frequency_seconds": 0.5,
    "fraud_injection_rate": 0.1,
    "batch_size": 5
  }'
```

**Configuration Parameters:**
- `frequency_seconds` (float): Time between batches in streaming mode (default: 1.0)
- `fraud_injection_rate` (float): Percentage of fraudulent transactions (0.0-1.0, default: 0.05)
- `batch_size` (int): Number of transactions per batch in streaming mode (default: 1)

### 7. Status Monitoring
**GET /status** - Get API operational status

```bash
curl http://localhost:8000/status
```

**Response:**
```json
{
  "streaming": false,
  "transactions_generated": 1247,
  "active_accounts": 156,
  "config": {
    "frequency_seconds": 1.0,
    "fraud_injection_rate": 0.05,
    "batch_size": 1
  }
}
```

## 🏦 Transaction Data Schema

Each transaction contains the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `transaction_id` | string | Unique transaction identifier (TXN_xxxxxxxx) |
| `account_id` | string | Account identifier (ACC_xxxxxx) |
| `branch_id` | integer | Bank branch ID (1-10) |
| `transaction_amount_vnd` | float | Transaction amount in Vietnamese Dong |
| `transaction_hour` | integer | Hour of transaction (0-23) |
| `transaction_timestamp` | string | ISO format timestamp |
| `location_city` | string | Transaction location |
| `device_id` | string | Device identifier |
| `biometric_failure_count` | integer | Number of biometric authentication failures |
| `transaction_frequency_5min` | integer | Number of transactions in last 5 minutes for this account |
| `total_loans_vnd` | float | Total loans for this account |
| `num_transactions` | integer | Total historical transactions for account |
| `npl_flag` | boolean | Non-performing loan flag |
| `total_deposits_vnd` | float | Total deposits for this account |
| `transaction_fees_vnd` | float | Transaction fees charged |

## 🚨 Fraud Patterns

The API generates realistic fraud patterns for testing:

### 1. Money Laundering
- **Characteristics**: Large amounts (300M-1B VND), off-hours transactions, high frequency
- **Detection Indicators**: Unusual transaction times, large amounts, rapid succession

### 2. Account Takeover
- **Characteristics**: New/unknown devices, multiple biometric failures, suspicious locations
- **Detection Indicators**: Device changes, authentication failures, location anomalies

### 3. Loan Fraud
- **Characteristics**: High loan amounts, new accounts with low transaction history
- **Detection Indicators**: High NPL rates, minimal transaction history, large loans

### 4. Fee Manipulation
- **Characteristics**: Small amounts with high frequency, unusual fee ratios
- **Detection Indicators**: High transaction frequency, abnormal fee patterns

## 💻 Usage Examples

### Python Client Example
```python
import requests
import json

# Get single transaction
response = requests.get('http://localhost:8000/transaction')
transaction = response.json()
print(json.dumps(transaction, indent=2))

# Get batch of transactions
response = requests.get('http://localhost:8000/transactions/50')
batch = response.json()
print(f"Received {batch['count']} transactions")

# Configure API
config = {
    "frequency_seconds": 0.5,
    "fraud_injection_rate": 0.1,
    "batch_size": 10
}
response = requests.post('http://localhost:8000/config', json=config)
print(response.json())
```

### JavaScript/Node.js Example
```javascript
const axios = require('axios');

// Get single transaction
async function getTransaction() {
    try {
        const response = await axios.get('http://localhost:8000/transaction');
        console.log(response.data);
    } catch (error) {
        console.error('Error:', error.message);
    }
}

// Stream transactions (using EventSource in browser)
const eventSource = new EventSource('http://localhost:8000/stream');
eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received transactions:', data.transactions.length);
};
```

### curl Examples
```bash
# Get 100 transactions
curl "http://localhost:8000/transactions/100" | jq '.'

# Update configuration
curl -X POST "http://localhost:8000/config" \
  -H "Content-Type: application/json" \
  -d '{"frequency_seconds": 2.0, "fraud_injection_rate": 0.15}'

# Check status
curl "http://localhost:8000/status" | jq '.'

# Stream data to file
curl -N "http://localhost:8000/stream" > transactions.jsonl
```

## 🔍 Data Analysis Tips

### Identifying Fraud Patterns
1. **High Frequency**: Look for `transaction_frequency_5min > 10`
2. **Large Amounts**: Monitor `transaction_amount_vnd > 100,000,000`
3. **Off Hours**: Check `transaction_hour` in ranges [0-4] or [22-23]
4. **New Devices**: Watch for device IDs starting with "DEV_NEW_"
5. **Authentication Issues**: Monitor `biometric_failure_count > 2`
6. **NPL Correlation**: Analyze relationship between `npl_flag` and transaction patterns

### Statistical Analysis
```python
import pandas as pd
import requests

# Collect data sample
transactions = []
for _ in range(1000):
    response = requests.get('http://localhost:8000/transaction')
    transactions.append(response.json())

df = pd.DataFrame(transactions)

# Basic statistics
print(df.describe())

# Fraud detection analysis
high_risk = df[
    (df['transaction_amount_vnd'] > 100_000_000) |
    (df['transaction_frequency_5min'] > 10) |
    (df['biometric_failure_count'] > 2)
]
print(f"High-risk transactions: {len(high_risk)} ({len(high_risk)/len(df)*100:.1f}%)")
```

## 🛡️ Security Considerations

⚠️ **Important**: This API is designed for development and testing purposes only.

- **No Authentication**: The API has no built-in security
- **CORS Enabled**: Allows requests from any origin
- **Data Privacy**: Generated data is synthetic - no real customer information
- **Production Use**: Not recommended for production environments without proper security measures

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using port 8000
   netstat -ano | findstr :8000
   # Kill the process or use a different port
   ```

2. **Dependency Issues**
   ```bash
   # Upgrade pip and reinstall
   python -m pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

3. **High Memory Usage**
   - Reduce `batch_size` in configuration
   - Implement data collection limits in your client
   - Monitor `active_accounts` in status endpoint

### Performance Optimization

- **Batch Processing**: Use `/transactions/{count}` instead of multiple single requests
- **Streaming**: Use `/stream` for continuous data collection
- **Configuration**: Adjust `frequency_seconds` and `batch_size` based on your needs

## 📊 Monitoring

Monitor API health using the `/status` endpoint:
- `transactions_generated`: Total transactions created
- `active_accounts`: Number of accounts with recent activity
- `streaming`: Current streaming status

## 🤝 Support

For issues or questions:
1. Check the interactive documentation at `/docs`
2. Verify configuration with `/config` endpoint
3. Monitor status with `/status` endpoint
4. Review this documentation for usage examples

## 📝 License

This project is for educational and testing purposes. Please ensure compliance with your organization's data usage policies.
