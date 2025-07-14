# VPBank Transaction Streaming Platform

A comprehensive real-time banking transaction data pipeline that generates realistic Vietnamese banking transactions with fraud detection patterns and streams them to AWS Kinesis for real-time analytics and fraud monitoring.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Transaction   │───▶│   Kinesis        │───▶│   Downstream        │
│   API Server    │    │   Producer       │    │   Analytics         │
│   (FastAPI)     │    │   (boto3)        │    │   (Lambda, etc.)    │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
```

## 🚀 Features

### Transaction API Server

- **Real-time Transaction Generation**: Generate single or batch Vietnamese banking transactions
- **Fraud Pattern Simulation**: 4 sophisticated fraud patterns with configurable injection rates
- **REST API**: Full OpenAPI documentation with Swagger UI
- **Vietnamese Banking Context**: VND currency, Vietnamese cities, realistic account patterns

### Kinesis Streaming Producer

- **AWS Kinesis Integration**: Real-time streaming to AWS Kinesis Data Streams
- **Fraud Detection Enhancement**: Enriches transactions with fraud detection features
- **Batch Processing**: Efficient batch sending with configurable parameters
- **Connection Testing**: Built-in health checks for API and Kinesis connectivity
- **Statistics Monitoring**: Real-time fraud rate monitoring and alerting

### Data Generation Features

- **Realistic Banking Data**: Vietnamese bank account patterns, cities, and transaction types
- **Fraud Simulation**: Money laundering, account takeover, loan fraud, and fee manipulation
- **Configurable Parameters**: Adjust fraud rates, batch sizes, and streaming intervals
- **High-Volume Capable**: Supports high-frequency transaction generation

## 📋 Prerequisites

- Python 3.8 or higher
- AWS Account with Kinesis access
- Git
- pip (Python package installer)

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/mqcuong1603/api_transactions_streaming.git
cd api_transactions_streaming
```

### 2. Create Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```env
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_DEFAULT_REGION=ap-southeast-1

# Kinesis Configuration
KINESIS_STREAM_NAME=Transactions

# API Configuration
TRANSACTION_API_URL=http://localhost:8000
```

## 🚀 Quick Start

### 1. Start the Transaction API Server

```bash
python api.py
```

The API will be available at:

- **Main endpoint**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

### 2. Test Kinesis Connection

```bash
python kinesis_producer.py test
```

Expected output:

```
✅ Kinesis Producer initialized
📍 Region: ap-southeast-1
🌊 Stream: Transactions
🔗 API URL: http://localhost:8000
🧪 Testing single transaction...
📤 TXN_00000001 | ✅ Normal | 5.2M VND | Shard: 0000
✅ Single transaction test successful!
```

### 3. Start Real-time Streaming

```bash
python kinesis_producer.py stream
```

Or with custom parameters:

```bash
python kinesis_producer.py stream 20 3 100
# batch_size=20, interval=3s, max_batches=100
```

## 📚 API Endpoints

### Transaction API Server

| Method | Endpoint                | Description                          |
| ------ | ----------------------- | ------------------------------------ |
| GET    | `/`                     | API information and status           |
| GET    | `/transaction`          | Get a single transaction             |
| GET    | `/transactions/{count}` | Get multiple transactions (max 1000) |
| GET    | `/stream`               | Start streaming transactions         |
| POST   | `/start`                | Start streaming mode                 |
| POST   | `/stop`                 | Stop streaming mode                  |
| GET    | `/status`               | Get API status and statistics        |
| GET    | `/config`               | Get current configuration            |
| POST   | `/config`               | Update configuration                 |

### Kinesis Producer CLI

| Command  | Usage                                                                     | Description                      |
| -------- | ------------------------------------------------------------------------- | -------------------------------- |
| `test`   | `python kinesis_producer.py test`                                         | Test API and Kinesis connections |
| `stream` | `python kinesis_producer.py stream [batch_size] [interval] [max_batches]` | Start streaming with parameters  |

## 🎯 Fraud Detection Patterns

The system generates 4 sophisticated fraud patterns:

### 1. Money Laundering (30% of fraud)

- **Characteristics**: Large amounts (300M-1B VND), off-hours transactions, high frequency
- **Kinesis Enrichment**: `high_amount_flag`, `off_hours_flag`, `high_frequency_flag`
- **Detection Signals**:
  - `transaction_amount_vnd > 300,000,000`
  - `transaction_frequency_5min > 15`
  - `transaction_hour in [1,2,3,22,23,24]`

### 2. Account Takeover (25% of fraud)

- **Characteristics**: New devices, multiple biometric failures, unusual locations
- **Kinesis Enrichment**: `suspicious_device_flag`
- **Detection Signals**:
  - `device_id` starts with "DEV_NEW_9"
  - `biometric_failure_count >= 3`

### 3. Loan Fraud (25% of fraud)

- **Characteristics**: High loan amounts, low transaction history, high NPL rates
- **Detection Signals**:
  - `total_loans_vnd > 500,000,000`
  - `num_transactions < 50`
  - `npl_flag = true`

### 4. Fee Manipulation (20% of fraud)

- **Characteristics**: Small amounts, very high frequency, unusual fee ratios
- **Detection Signals**:
  - `transaction_frequency_5min > 12`
  - High `transaction_fees_vnd` to amount ratio

## � Configuration Examples

### Update API Configuration

```bash
curl -X POST "http://localhost:8000/config" \
     -H "Content-Type: application/json" \
     -d '{
       "frequency_seconds": 0.5,
       "fraud_injection_rate": 0.1,
       "batch_size": 5
     }'
```

### Stream with Custom Parameters

```bash
# High-frequency streaming (batch=50, interval=1s, max=1000 batches)
python kinesis_producer.py stream 50 1 1000

# Low-frequency streaming (batch=5, interval=10s, unlimited)
python kinesis_producer.py stream 5 10
```

## 📊 Monitoring and Alerts

### Real-time Statistics

The Kinesis producer provides real-time monitoring:

```
📦 Batch sent: 20/20 success | 3 fraud detected
📈 Total: 500 transactions | 25 fraud (5.0%)
🚨 HIGH FRAUD ALERT: 8/20 transactions in this batch!
```

### Key Metrics Tracked

- **Transaction Volume**: Total transactions processed
- **Fraud Rate**: Percentage of fraudulent transactions
- **Batch Success Rate**: Kinesis delivery success rate
- **High Fraud Alerts**: Batches with >30% fraud rate
- **Shard Distribution**: Kinesis shard utilization

## 🛠️ Development & Testing

### Generate Test Data

```bash
# Generate sample CSV data
python generate_banking_csv.py
```

### Run Development Server

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Test Individual Components

```python
# Test single transaction
import requests
response = requests.get("http://localhost:8000/transaction")
print(response.json())

# Test Kinesis connectivity
from kinesis_producer import VPBankKinesisProducer
producer = VPBankKinesisProducer()
producer.test_connections()
```

## � Security & Best Practices

### Environment Variables

- Store AWS credentials in `.env` file (never commit to git)
- Use IAM roles with minimal Kinesis permissions
- Rotate access keys regularly

### AWS IAM Permissions

Minimum required permissions for Kinesis:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "kinesis:PutRecord",
        "kinesis:PutRecords",
        "kinesis:DescribeStream"
      ],
      "Resource": "arn:aws:kinesis:ap-southeast-1:*:stream/Transactions"
    }
  ]
}
```

### Data Privacy

- Uses synthetic data only
- No real banking information
- Safe for development and testing

## 🐛 Troubleshooting

### Common Issues

**AWS Credentials Error:**

```bash
# Check .env file exists and contains valid credentials
cat .env

# Verify AWS CLI access
aws kinesis describe-stream --stream-name Transactions
```

**Kinesis Stream Not Found:**

```bash
# Create Kinesis stream
aws kinesis create-stream --stream-name Transactions --shard-count 1

# Check stream status
aws kinesis describe-stream --stream-name Transactions
```

**API Connection Failed:**

```bash
# Check if API server is running
curl http://localhost:8000/status

# Start API server if not running
python api.py
```

**High Memory Usage:**

```bash
# Reduce batch size and increase interval
python kinesis_producer.py stream 10 5
```

## 📈 Performance Optimization

### Recommended Settings

| Use Case     | Batch Size | Interval | Max Batches |
| ------------ | ---------- | -------- | ----------- |
| Development  | 5-10       | 5-10s    | 50-100      |
| Testing      | 20-50      | 1-3s     | 500-1000    |
| Load Testing | 100-500    | 0.1-1s   | 10000+      |

### Monitoring Performance

```bash
# Monitor with built-in statistics
python kinesis_producer.py stream 20 2 1000

# Check AWS CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Kinesis \
  --metric-name IncomingRecords \
  --dimensions Name=StreamName,Value=Transactions
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/mqcuong1603/api_transactions_streaming/issues)
- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Contact**: mqcuong1603@gmail.com

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) for the API server
- [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) for AWS Kinesis integration
- Data generation with [NumPy](https://numpy.org/) and realistic Vietnamese banking patterns
- AWS Kinesis for real-time data streaming

---

**⚠️ Important**: This system generates synthetic banking data for testing and development purposes only. Do not use with real financial data or in production environments without proper security measures.
