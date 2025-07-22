# Feed-Comparator
The Feed Comparator is a debugging tool designed to validate the accuracy of market data after updates, ensuring backward compatibility and protecting traders from acting on incorrect information. It automates the comparison of two large market data CSV files—retrieved from Amazon S3 using Boto3—and generates a detailed difference report that is uploaded back to S3.

The script identifies missed updates, discrepancies in bid/ask books, and skipped assets, using Python dictionaries keyed by asset ID to efficiently track matched and unmatched updates. This structure accommodates unordered asset delivery while preserving the sequence of updates per asset.

## Prerequisites

Before running the Feed Comparator, ensure you have the following:

- **Python 3.7+**
- **Boto3** (`pip install boto3`)
- **AWS credentials** configured with access to the relevant S3 bucket
- IAM Permissions to read from and write to your S3 bucket

Make sure your AWS credentials are set either via environment variables, `~/.aws/credentials`, or IAM role (if running on AWS infrastructure).

## Optionality
Depending on your CSV table structure you can edit this information with your own column tables. 

````

try:
            asset_id = row[idx_map['asset_id']]
            asset_data[asset_id].append((
                row[idx_map['Date']],
                row[idx_map['Open']],
                row[idx_map['High']],
                row[idx_map['Low']],
                row[idx_map['Close']],
                row[idx_map['Volume']]
            ))



````

## Example Data

````
asset_id,Date,Open,High,Low,Close,Volume
AAPL,2025-07-22,190.12,191.23,188.76,190.78,54200000
MSFT,2025-07-22,345.66,349.00,342.50,347.89,38120000
GOOG,2025-07-22,132.45,133.10,131.20,132.99,20150000
````

````
asset_id,Date,Open,High,Low,Close,Volume
AAPL,2025-07-22,190.12,191.23,188.76,190.79,54200000
MSFT,2025-07-22,345.66,349.00,342.50,347.89,38120000
GOOG,2025-07-22,132.45,133.10,131.20,133.00,20150000
````


