# Banking Transaction Data API

A FastAPI-based service that generates realistic banking transaction data with built-in fraud patterns for testing fraud detection systems.

## 🚀 Features

- **Real-time Transaction Generation**: Generate single or batch transactions
- **Fraud Pattern Simulation**: 4 types of fraud patterns with configurable injection rates
- **Streaming API**: Server-sent events for continuous data flow
- **Vietnamese Banking Context**: VND currency, Vietnamese cities, realistic data patterns
- **Configurable Parameters**: Adjust fraud rates, frequency, and batch sizes
- **REST API**: Full OpenAPI documentation with Swagger UI

## 📋 Prerequisites

- Python 3.8 or higher
- Git
- pip (Python package installer)

## 🔧 Installation from GitHub

### 1. Clone the Repository

```bash
git clone https://github.com/mqcuong1603/api_transactions_streaming.git
cd api_transactions_streaming
```

### 2. Create Virtual Environment (Recommended)

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

### 4. Verify Installation

```bash
python api.py
```

You should see:

```
INFO:     Started server process [xxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## 🚀 Quick Start

### Start the API Server

```bash
python api.py
```

### Test the API

Open your browser and visit:

- **Main endpoint**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

### Get a Single Transaction

```bash
curl http://localhost:8000/transaction
```

### Get Multiple Transactions

```bash
curl http://localhost:8000/transactions/10
```

## 📚 API Endpoints

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

## 🔧 Configuration

### Default Configuration

```json
{
  "frequency_seconds": 1.0,
  "fraud_injection_rate": 0.05,
  "batch_size": 1
}
```

### Update Configuration

```bash
curl -X POST "http://localhost:8000/config" \
     -H "Content-Type: application/json" \
     -d '{
       "frequency_seconds": 0.5,
       "fraud_injection_rate": 0.1,
       "batch_size": 5
     }'
```

## 🎯 Fraud Patterns

The API generates 4 types of fraud patterns:

### 1. Money Laundering (30% of fraud)

- **Characteristics**: Large amounts (300M-1B VND), off-hours transactions, high frequency
- **Detection signals**: `transaction_amount_vnd > 300M`, `transaction_frequency_5min > 15`

### 2. Account Takeover (25% of fraud)

- **Characteristics**: New devices, multiple biometric failures, unusual locations
- **Detection signals**: `device_id` starts with "DEV_NEW_9", `biometric_failure_count >= 3`

### 3. Loan Fraud (25% of fraud)

- **Characteristics**: High loan amounts, low transaction history, high NPL rates
- **Detection signals**: `total_loans_vnd > 500M`, `num_transactions < 50`, `npl_flag = true`

### 4. Fee Manipulation (20% of fraud)

- **Characteristics**: Small amounts, very high frequency, unusual fee ratios
- **Detection signals**: `transaction_frequency_5min > 12`, high `transaction_fees_vnd` ratio

## 📊 Usage Examples

### Python Client

```python
import requests
import json

# Get single transaction
response = requests.get("http://localhost:8000/transaction")
transaction = response.json()
print(json.dumps(transaction, indent=2))

# Get batch of transactions
response = requests.get("http://localhost:8000/transactions/100")
batch = response.json()
print(f"Received {batch['count']} transactions")

# Update configuration
config = {
    "frequency_seconds": 0.1,
    "fraud_injection_rate": 0.2,
    "batch_size": 10
}
response = requests.post("http://localhost:8000/config", json=config)
print(response.json())
```

### JavaScript Client

```javascript
// Get single transaction
fetch("http://localhost:8000/transaction")
  .then((response) => response.json())
  .then((data) => console.log(data));

// Stream transactions
const eventSource = new EventSource("http://localhost:8000/stream");
eventSource.onmessage = function (event) {
  const data = JSON.parse(event.data);
  console.log("Received transactions:", data.transactions.length);
};
```

### curl Examples

```bash
# Get API status
curl http://localhost:8000/status

# Start streaming
curl -X POST http://localhost:8000/start

# Stop streaming
curl -X POST http://localhost:8000/stop

# Get 50 transactions
curl http://localhost:8000/transactions/50
```

## 🛠️ Development

### Running in Development Mode

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run tests (create test files as needed)
pytest
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t banking-api .
docker run -p 8000:8000 banking-api
```

## 📈 Performance & Scaling

### Performance Tips

- Use batch endpoints for bulk data collection
- Adjust `frequency_seconds` for optimal streaming rate
- Monitor memory usage with high-frequency streaming
- Use appropriate `batch_size` for your use case

### Resource Usage

- **Memory**: ~50MB base + ~1KB per active account
- **CPU**: Minimal, scales with request frequency
- **Network**: ~2KB per transaction

## 🔒 Security Considerations

⚠️ **Important**: This API is designed for testing and development only.

- **CORS**: Currently allows all origins (`*`)
- **Authentication**: No authentication implemented
- **Rate Limiting**: No rate limiting implemented
- **Data Privacy**: Uses synthetic data only

For production use, implement:

- Authentication and authorization
- Rate limiting
- Input validation
- Logging and monitoring
- Proper CORS configuration

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**

```bash
# Find process using port 8000
netstat -ano | findstr :8000
# Kill the process or use different port
uvicorn api:app --port 8001
```

**Import errors:**

```bash
# Ensure virtual environment is activated
pip install -r requirements.txt
```

**Memory issues with streaming:**

- Reduce `batch_size`
- Increase `frequency_seconds`
- Monitor with `/status` endpoint

### Logs

Check console output for detailed logging:

```
INFO:     Transaction streaming started
INFO:     Configuration updated: {...}
ERROR:    Stream error: ...
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

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Data generation with [NumPy](https://numpy.org/)
- Realistic Vietnamese banking context

---

**Note**: This API generates synthetic data for testing purposes only. Do not use with real financial data.
8
