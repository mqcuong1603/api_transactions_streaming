import boto3
import json
import requests
import time
import os
from datetime import datetime, UTC
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VPBankKinesisProducer:
    def __init__(self):
        # AWS Configuration
        self.region = os.getenv('AWS_DEFAULT_REGION', 'ap-southeast-1')
        self.stream_name = os.getenv('KINESIS_STREAM_NAME', 'Transactions')
        self.api_url = os.getenv('TRANSACTION_API_URL', 'http://localhost:8000')
        
        # Initialize Kinesis client
        self.kinesis = boto3.client(
            'kinesis',
            region_name=self.region,
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        print(f"✅ Kinesis Producer initialized")
        print(f"📍 Region: {self.region}")
        print(f"🌊 Stream: {self.stream_name}")
        print(f"🔗 API URL: {self.api_url}")
    
    def test_connections(self):
        """Test both API and Kinesis connections"""
        print("\n🧪 Testing connections...")
        
        # Test Transaction API
        try:
            response = requests.get(f"{self.api_url}/status", timeout=5)
            if response.status_code == 200:
                print("✅ Transaction API: Connected")
            else:
                print(f"❌ Transaction API: Error {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Transaction API: Connection failed - {e}")
            return False
        
        # Test Kinesis Stream
        try:
            stream_info = self.kinesis.describe_stream(StreamName=self.stream_name)
            status = stream_info['StreamDescription']['StreamStatus']
            print(f"✅ Kinesis Stream: {status}")
            
            if status != 'ACTIVE':
                print(f"⚠️  Stream not active. Current status: {status}")
                return False
                
        except Exception as e:
            print(f"❌ Kinesis Stream: Connection failed - {e}")
            return False
        
        print("🎉 All connections successful!\n")
        return True
    
    def enrich_transaction(self, transaction):
        """Add metadata to transaction before sending to Kinesis"""
        enriched = {
            **transaction,
            'kinesis_timestamp': datetime.now(UTC).isoformat(),
            'source': 'vpbank_transaction_api',
            'region': self.region,
            'stream_name': self.stream_name,
            # Add fraud detection features
            'high_amount_flag': transaction['transaction_amount_vnd'] > 300_000_000,
            'off_hours_flag': transaction['transaction_hour'] in [1, 2, 3, 22, 23, 24],
            'suspicious_device_flag': 'DEV_NEW_' in transaction.get('device_id', ''),
            'high_frequency_flag': transaction.get('transaction_frequency_5min', 0) > 10
        }
        return enriched
    
    def send_single_transaction(self, transaction):
        """Send single transaction to Kinesis"""
        try:
            # Enrich transaction with metadata
            enriched_transaction = self.enrich_transaction(transaction)
            
            # Send to Kinesis
            response = self.kinesis.put_record(
                StreamName=self.stream_name,
                Data=json.dumps(enriched_transaction, default=str),
                PartitionKey=transaction['account_id']  # Use account_id for partitioning
            )
            
            # Success feedback
            shard_id = response['ShardId']
            sequence_number = response['SequenceNumber']
            
            fraud_indicator = "🚨 FRAUD" if transaction.get('is_fraud', False) else "✅ Normal"
            amount_vnd = transaction['transaction_amount_vnd'] / 1_000_000  # Convert to millions
            
            print(f"📤 {transaction['transaction_id']} | {fraud_indicator} | {amount_vnd:.1f}M VND | Shard: {shard_id[-4:]}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send transaction {transaction.get('transaction_id', 'unknown')}: {e}")
            return False
    
    def send_batch_transactions(self, transactions):
        """Send batch of transactions to Kinesis"""
        records = []
        
        for transaction in transactions:
            enriched = self.enrich_transaction(transaction)
            records.append({
                'Data': json.dumps(enriched, default=str),
                'PartitionKey': transaction['account_id']
            })
        
        try:
            response = self.kinesis.put_records(
                Records=records,
                StreamName=self.stream_name
            )
            
            # Check for failures
            failed_count = response['FailedRecordCount']
            success_count = len(transactions) - failed_count
            
            fraud_count = sum(1 for t in transactions if t.get('is_fraud', False))
            
            print(f"📦 Batch sent: {success_count}/{len(transactions)} success | {fraud_count} fraud detected")
            
            if failed_count > 0:
                print(f"⚠️  {failed_count} records failed")
            
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Batch send failed: {e}")
            return False
    
    def start_streaming(self, batch_size=10, interval_seconds=5, max_batches=None):
        """Start continuous streaming from API to Kinesis"""
        
        if not self.test_connections():
            print("❌ Connection test failed. Please check your configuration.")
            return
        
        print(f"🚀 Starting VPBank fraud detection streaming...")
        print(f"📊 Batch size: {batch_size} transactions")
        print(f"⏱️  Interval: {interval_seconds} seconds")
        print(f"🛑 Press Ctrl+C to stop\n")
        
        batch_count = 0
        total_transactions = 0
        total_fraud = 0
        
        try:
            while True:
                # Check if we've reached max batches
                if max_batches and batch_count >= max_batches:
                    print(f"🏁 Reached maximum batches ({max_batches}). Stopping.")
                    break
                
                # Get transactions from API
                try:
                    response = requests.get(
                        f"{self.api_url}/transactions/{batch_size}",
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        transactions = data['transactions']
                        
                        if transactions:
                            # Send to Kinesis
                            if self.send_batch_transactions(transactions):
                                batch_count += 1
                                total_transactions += len(transactions)
                                batch_fraud = sum(1 for t in transactions if t.get('is_fraud', False))
                                total_fraud += batch_fraud
                                
                                # Show running statistics
                                fraud_rate = (total_fraud / total_transactions * 100) if total_transactions > 0 else 0
                                print(f"📈 Total: {total_transactions} transactions | {total_fraud} fraud ({fraud_rate:.1f}%)")
                                
                                # Alert for high fraud batch
                                if batch_fraud >= batch_size * 0.3:  # 30% fraud in batch
                                    print(f"🚨 HIGH FRAUD ALERT: {batch_fraud}/{batch_size} transactions in this batch!")
                            
                        else:
                            print("⚠️  No transactions received from API")
                    
                    else:
                        print(f"❌ API Error: {response.status_code}")
                
                except requests.exceptions.RequestException as e:
                    print(f"❌ API Request failed: {e}")
                
                # Wait before next batch
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Streaming stopped by user")
        except Exception as e:
            print(f"\n❌ Streaming error: {e}")
        
        finally:
            print(f"\n📊 Final Statistics:")
            print(f"🔢 Total Batches: {batch_count}")
            print(f"💳 Total Transactions: {total_transactions}")
            print(f"🚨 Total Fraud: {total_fraud}")
            if total_transactions > 0:
                fraud_rate = total_fraud / total_transactions * 100
                print(f"📈 Overall Fraud Rate: {fraud_rate:.2f}%")
    
    def test_single_transaction(self):
        """Test sending a single transaction"""
        print("🧪 Testing single transaction...")
        
        try:
            response = requests.get(f"{self.api_url}/transaction")
            if response.status_code == 200:
                transaction = response.json()
                success = self.send_single_transaction(transaction)
                
                if success:
                    print("✅ Single transaction test successful!")
                    return True
                else:
                    print("❌ Single transaction test failed!")
                    return False
            else:
                print(f"❌ Failed to get transaction from API: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False

# CLI Interface
if __name__ == "__main__":
    producer = VPBankKinesisProducer()
    
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            # Test connections and single transaction
            producer.test_single_transaction()
            
        elif command == "stream":
            # Start streaming with custom parameters
            batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            interval = int(sys.argv[3]) if len(sys.argv) > 3 else 5
            max_batches = int(sys.argv[4]) if len(sys.argv) > 4 else None
            
            producer.start_streaming(batch_size, interval, max_batches)
            
        else:
            print("Usage: python kinesis_producer.py [test|stream] [batch_size] [interval] [max_batches]")
    
    else:
        # Default: Start streaming
        producer.start_streaming()