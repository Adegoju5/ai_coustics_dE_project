# ai_coustics_dE_project

## Audio Processing and Storage

This script allows you to scrape a webpage for audio links, download the audio files, upload them to Google Cloud Storage, and store metadata in Google BigQuery.

## Prerequisites

Before running the script, make sure you have the following:

### Google Cloud Platform (GCP) Account:

- Create a GCP account if you don't have one: [Google Cloud Platform](https://cloud.google.com/).
- Set up a GCP project and enable the Cloud Storage and BigQuery APIs.

### Service Account Key:

- Create a service account key with access to Cloud Storage and BigQuery.
- Download the JSON key file and note its path and set it as key_file_path variable.

### Python Dependencies:
Install the required Python libraries using the following command:
```bash
pip install google-cloud-storage google-cloud-bigquery google-cloud-core pydub beautifulsoup4 requests os
```
# Script Configuration

Before running the script, make sure to configure the following variables in the script with your desired values:

- `bucket_name`: Update with your preferred bucket name.
- `project_id`: Update with your Google Cloud Platform (GCP) project ID.
- `table_id`: Update with the desired BigQuery table ID.

# Webpage URL

Specify the URL of the webpage you want to scrape for audio links.

# Execution

Run the script using the following command:

```bash
python audio_processing.py
```

# Output

The script performs the following actions:

- Downloads audio files.
- Uploads the downloaded audio files to Google Cloud Storage (GCS).
- Stores metadata in Google BigQuery.

# Database System

This script utilizes Google BigQuery as the database system for storing audio metadata. BigQuery is a fully-managed, serverless data warehouse that enables super-fast SQL queries using the processing power of Google's infrastructure.

By leveraging BigQuery, the script ensures efficient and scalable storage of audio metadata, allowing for quick and powerful data analysis through SQL queries.

# Schema for `audio_metadata` Table

The script uses the following schema for the `audio_metadata` table in Google BigQuery:

- `gcp_url` (STRING, REQUIRED): GCP Storage URL of the audio file.
- `file_name` (STRING, REQUIRED): Name of the audio file.
- `duration_ms` (INTEGER, REQUIRED): Duration of the audio in milliseconds.
- `loudness` (FLOAT, REQUIRED): Loudness of the audio in dBFS.
- `classification` (STRING, REQUIRED): Classification of the audio (High Energy, Low Energy, Medium Energy).

# Upsert in BigQuery

The script incorporates an upsert (insert or update) operation when storing metadata in Google BigQuery. This methodology ensures that:

- If a record with the same `gcp_url` already exists, it will be updated.
- If a record with the specified `gcp_url` does not exist, a new record will be inserted.

# Storage System

Google Cloud Storage (GCS) is the chosen storage system for storing the audio files in this project. GCS is a scalable and highly available object storage service.

The script dynamically updates the `bucket_name` variable to specify the GCS bucket where the audio files are uploaded. This ensures flexibility and adaptability in managing storage locations based on your project's needs.

# On Preferred Storage Systems

I would use the combination of cloud storage platforms(Google Cloud Storage for storing the audio files and Google BigQuery as the database system for storing audio metadata) as used in the python script, Because they provide specialized services that allows you to build a scalable and efficient system for managing audio data and its metadata in a production environment for subsequent machine learning tasks.

