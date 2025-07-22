#!/usr/bin/env python3

import io
import csv
import boto3
from botocore.exceptions import ClientError
import time
from tqdm import tqdm
import sys
import argparse
from collections import defaultdict

def bucket_exist(bucket_name):
    s3 = boto3.client('s3')
    try:
        s3.head_bucket(Bucket=bucket_name)
        return True
    except ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            print(f"Bucket {bucket_name} not found")
        else:
            print(f"access error unknow issue {e}")
            return False

def list_bucket_object(bucket_name):
    s3= boto3.resource('s3')

    bucket = s3.Bucket(bucket_name)
    
    objects = list(bucket.objects.all())
    print(f"Objects in bucket {bucket_name}")
    for idx, obj in enumerate(objects):
        print(f"[{idx}] {obj.key}")

    return objects

def choose_file_from_s3(bucket_name, objects):
    try:
        idx = int(input(f"Select a file index from 0 to {len(objects)-1}: "))
        selected_key = objects[idx].key
        print(f"Selected: {selected_key}")
        return selected_key
    except (ValueError, IndexError):
        print("Ivalid selection")
        return None

def read_csv_from_s3(bucket_name, key):
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket_name, Key=key)
    content = obj['Body'].read().decode('utf-8')
    return csv.reader(io.StringIO(content))

def load_csv_line(csv_lines):
    asset_data = defaultdict(list)
    header = next(csv_lines)
    idx_map = {k.strip(): i for i, k in enumerate(header)}

    required_keys = ['asset_id', 'Date', 'Open', 'Close', 'High', 'Low', 'Volume']


    for row in csv_lines:
        if not row or len(row) < len(required_keys):
            print(f"Warning skipping malformed row: {row}")
            continue
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
        except Exception as e:
            print(f"[ERROR] Failed to parse row: {row} -> {e}")
            continue
    return asset_data
def compare_feed_lines(feed1, feed2):
    diffs = []
    unmatched1 = defaultdict(list)
    unmatched2 = defaultdict(list)

    all_assets = set(feed1.keys()) | set(feed2.keys())

    for asset in all_assets:
        list1 = feed1.get(asset, [])
        list2 = feed2.get(asset, [])
        min_len = min(len(list1), len(list2))

        for i in range(min_len):
            if list1[i] != list2[i]:
                diffs.append({
                    'asset_id': asset,
                    'index': i,
                    'feed1': list1[i],
                    'feed2': list2[i]
                })

        if len(list1) > min_len:
            unmatched1[asset].extend(list1[min_len:])
        if len(list2) > min_len:
            unmatched2[asset].extend(list2[min_len:])
    return diffs, unmatched1, unmatched2

def write_diffs_csv(diffs, unmatched1, unmatched2, output="diff_report.csv"):
    with open(output, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Type", "Asset ID", "Index", "Feed1", "Feed2"])

        for d in diffs:
            writer.writerow(["Diff", d['asset_id'], d['index'], d['feed1'], d['feed2']])
    
        for asset, entries in unmatched1.items():
            for e in entries:
                writer.writerow(["Missing in Feed 1", asset, "", e, ""])

        s3 = boto3.resource('s3')
        s3.meta.client.upload_file(output, 'myorderbook', 'diff_report.csv')



def main():
    s3 = boto3.resource('s3')

    bucket_name = input("Please enter S3 bucket name")
    if not bucket_exist(bucket_name):
        return

    objects = list_bucket_object(bucket_name)

    if not objects:
        print(f"No objects in {bucket_name}")
        return

    print("Choose first csv")
    key1 = choose_file_from_s3(bucket_name, objects)
    if not key1:
        return

    print("Choose second csv")
    key2 = choose_file_from_s3(bucket_name, objects)
    if not key2:
        return

    try:
        reader1_content = list(read_csv_from_s3(bucket_name, key1))
        reader2_content = list(read_csv_from_s3(bucket_name, key2))

        print(100 * '_')
        print(f"contents of {key1}")
        print(100 * '_')
        for row in reader1_content:
            print(row)

        print(100 * '_')
        print(f"contents of {key2}")
        print(100 * '_')
        for row in reader2_content:
            print(row)

    except Exception as e:
        print(f"error reading from s3 {e}")
        return


    choice = input("would you like to continute (y/n)").strip().lower()
    if choice == 'y':
        for i in tqdm(range(100)):
            time.sleep(0.05)
        print("feed complete")
        feed1 = load_csv_line(iter(reader1_content))
        feed2 = load_csv_line(iter(reader2_content))
        diffs, unmatched1, unmatched2 = compare_feed_lines(feed1, feed2)
        write_diffs_csv(diffs, unmatched1, unmatched2)


    else:
        print("aborted")

if __name__ == "__main__":
    main()
