import os
import requests
from google.cloud import storage, bigquery
from pydub import AudioSegment
from bs4 import BeautifulSoup


def find_audio_links(url):
    """
    Scrapes a webpage and extracts unique audio file links.

    Args:
        url (str): The URL of the webpage.

    Returns:
        list: A list of unique audio file links.
    """
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        all_links = soup.find_all('a', href=True)
        audio_extensions = ['.mp3', '.wav', '.ogg', '.flac', '.aac']
        audio_links = [link['href'] for link in all_links if any(link['href'].lower().endswith(ext) for ext in audio_extensions)]
        unique_audio_links = set(audio_links)
        return list(unique_audio_links)
    else:
        print(f"Error: Unable to fetch content from {url}. Status code: {response.status_code}")
        return []
def upload_to_gcp_storage(key_file_path, bucket_name, local_file_path, remote_file_name):
    """
    Uploads a file to a GCP Storage bucket.

    Args:
        key_file_path : key path to google cloud connection
        bucket_name (str): The name of the GCP Storage bucket.
        local_file_path (str): The local path to the file to upload.
        remote_file_name (str): The name to give the file in the bucket.

    Returns:
        str: The public URL of the uploaded file.
    """
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_file_path

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(remote_file_name)
    blob.upload_from_filename(local_file_path)
    return blob.public_url


def get_audio_metadata(local_file_path):
    """
    Retrieves metadata (duration and loudness) of an audio file.

    Args:
        local_file_path (str): The local path to the audio file.

    Returns:
        tuple: A tuple containing duration (in milliseconds) and loudness (in dBFS).
    """
    audio = AudioSegment.from_file(local_file_path)
    duration_ms = len(audio)
    loudness = audio.dBFS
    return duration_ms, loudness


def classify_audio(duration_ms, loudness):
    """
    Classifies audio based on duration and loudness.

    Args:
        duration_ms (int): Duration of the audio in milliseconds.
        loudness (float): Loudness of the audio in dBFS.

    Returns:
        str: The classification of the audio.
    """
    if duration_ms < 60000 and loudness > -20:
        return 'High Energy'
    elif duration_ms >= 60000 and loudness <= -20:
        return 'Low Energy'
    else:
        return 'Medium Energy'


def insert_into_bigquery(key_file_path, table_id,gcp_url, file_name, duration_ms, loudness, classification):
    """
    Inserts or updates audio metadata into BigQuery.

    Args:
        key_file_path : key path to google cloud connection
        table_id: The target table in bigquery
        gcp_url (str): The GCP Storage URL of the audio file.
        file_name (str): The name of the audio file.
        duration_ms (int): Duration of the audio in milliseconds.
        loudness (float): Loudness of the audio in dBFS.
        classification (str): The classification of the audio.

    Returns:
        str: A message indicating the success of the operation.
    """
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_file_path

    client = bigquery.Client()
    table_ref = client.dataset(table_id.split('.')[1]).table(table_id.split('.')[2])

    try:
        client.get_table(table_ref)
    except:
        schema = [
            bigquery.SchemaField("gcp_url", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("file_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("duration_ms", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("loudness", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("classification", "STRING", mode="REQUIRED"),
        ]
        table = bigquery.Table(table_ref, schema=schema)
        client.create_table(table)

    query = f'SELECT COUNT(*) FROM `{table_id}` WHERE gcp_url = @gcp_url'
    query_params = [bigquery.ScalarQueryParameter("gcp_url", "STRING", gcp_url)]
    job_config = bigquery.QueryJobConfig(query_parameters=query_params)
    query_job = client.query(query, job_config=job_config)
    existing_rows = list(query_job.result())[0][0]

    if existing_rows == 0:
        query = f'''
            INSERT INTO `{table_id}` (gcp_url, file_name, duration_ms, loudness, classification)
            VALUES (@gcp_url, @file_name, @duration_ms, @loudness, @classification)
        '''
    else:
        query = f'''
            UPDATE `{table_id}` SET
            file_name = @file_name,
            duration_ms = @duration_ms,
            loudness = @loudness,
            classification = @classification
            WHERE gcp_url = @gcp_url
        '''

    query_params = [
        bigquery.ScalarQueryParameter("gcp_url", "STRING", gcp_url),
        bigquery.ScalarQueryParameter("file_name", "STRING", file_name),
        bigquery.ScalarQueryParameter("duration_ms", "INTEGER", duration_ms),
        bigquery.ScalarQueryParameter("loudness", "FLOAT", loudness),
        bigquery.ScalarQueryParameter("classification", "STRING", classification),
    ]

    job_config = bigquery.QueryJobConfig(query_parameters=query_params)
    query_job = client.query(query, job_config=job_config)

    return f"Data inserted/updated in BigQuery. gcp_url: {gcp_url}, Classification: {classification}"


# Example usage:
key_file_path = "/Users/debowalealex/Downloads/nth-glider-362309-06dfa4dc6384.json"
bucket_name = 'adegoju_bucket'
project_id = 'nth-glider-362309'
table_id = 'nth-glider-362309.audio_files.audio_metadata'

# Example usage for testing purposes
url_to_scrape = 'https://www.naijaloaded.com.ng/download-music/victor-ad-ft-phyno-anymore'
audio_links = find_audio_links(url_to_scrape)



for each_link in audio_links:
    # Download the audio file
    audio_response = requests.get(each_link)

    # Extract the file name from the URL
    file_name = os.path.basename(each_link)

    # Define the local path to save the file temporarily
    local_file_path = f'temporary_{file_name}'

    # Save the audio file locally
    with open(local_file_path, 'wb') as file:
        file.write(audio_response.content)

    # Upload the file to GCP Storage
    gcp_url = upload_to_gcp_storage(bucket_name, local_file_path, file_name)

    # Get audio metadata
    duration_ms, loudness = get_audio_metadata(local_file_path)

    # Classify the audio
    classification = classify_audio(duration_ms, loudness)

    # Insert data into BigQuery
    result = insert_into_bigquery(gcp_url, file_name, duration_ms, loudness, classification)


    # Clean up: Remove the temporary local file
    os.remove(local_file_path)