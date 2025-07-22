# Feed-Comparator
The Feed Comparator is a debugging tool designed to validate the accuracy of market data after updates, ensuring backward compatibility and protecting traders from acting on incorrect information. It automates the comparison of two large market data CSV files—retrieved from Amazon S3 using Boto3—and generates a detailed difference report that is uploaded back to S3.

The script identifies missed updates, discrepancies in bid/ask books, and skipped assets, using Python dictionaries keyed by asset ID to efficiently track matched and unmatched updates. This structure accommodates unordered asset delivery while preserving the sequence of updates per asset.
