#!/usr/bin/env python3
# Script to export tasks to CSV and upload to GCS bucket

import requests
import csv
import json
import io
import os
from datetime import datetime
from google.cloud import storage

# Configuration
BUCKET_NAME = "cursor-cs436-minitasks-csv-exports"
API_ENDPOINT = "http://34.45.173.31/api/tasks"  # GKE service external IP

def fetch_tasks():
    """Fetch all tasks from the API"""
    try:
        response = requests.get(API_ENDPOINT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching tasks: {e}")
        return None

def convert_to_csv(tasks):
    """Convert tasks JSON to CSV format"""
    if not tasks:
        return None
    
    # Create a file-like object to write CSV data
    csv_file = io.StringIO()
    
    # Assume all tasks have the same structure, so get field names from the first task
    fieldnames = tasks[0].keys()
    
    # Create CSV writer
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    
    # Write each task as a row
    for task in tasks:
        writer.writerow(task)
    
    csv_content = csv_file.getvalue()
    csv_file.close()
    
    return csv_content

def upload_to_gcs(csv_content):
    """Upload CSV content to Google Cloud Storage bucket"""
    if not csv_content:
        print("No CSV content to upload")
        return False
    
    try:
        # Create a client
        storage_client = storage.Client()
        
        # Get the bucket
        bucket = storage_client.bucket(BUCKET_NAME)
        
        # Create a blob with today's date in the filename
        today = datetime.now().strftime("%Y-%m-%d")
        blob_name = f"tasks_export_{today}.csv"
        
        blob = bucket.blob(blob_name)
        
        # Upload the CSV content
        blob.upload_from_string(csv_content, content_type="text/csv")
        
        print(f"Successfully uploaded {blob_name} to {BUCKET_NAME}")
        return True
    
    except Exception as e:
        print(f"Error uploading to GCS: {e}")
        return False

def main():
    # Fetch tasks from API
    print("Fetching tasks from API...")
    tasks = fetch_tasks()
    
    if not tasks:
        print("No tasks to export")
        return
    
    # Convert to CSV
    print("Converting tasks to CSV...")
    csv_content = convert_to_csv(tasks)
    
    # Upload to GCS
    print("Uploading CSV to Cloud Storage...")
    upload_to_gcs(csv_content)

if __name__ == "__main__":
    main() 