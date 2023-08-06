from google.cloud import storage
from google.cloud import bigquery
from google.oauth2 import service_account
from dataclasses import dataclass
import os

@dataclass
class GCSBucket:
    project_id: str
    bucket_name: str
    blob_name: str
    blob_directory: str
    dataset_id: str = None
    table_id: str = None
    temp_file_path: str = "temp/temp.parquet"
    client: storage.Client = None
    bigquery_client: bigquery.Client = None

    def create_client(self, key_path) -> None:
        project_id = self.project_id
        cred = service_account.Credentials.from_service_account_file(key_path, scopes=[
            "https://www.googleapis.com/auth/cloud-platform"])
        self.client = storage.Client(project=project_id, credentials=cred)
        self.bigquery_client = bigquery.Client(
            credentials=cred,
            project=cred.project_id
        )

    def uploading(self) -> None:
        bucket = self.client.get_bucket(self.bucket_name)
        blob = bucket.blob(f"{self.blob_directory}{self.blob_name}")
        blob.upload_from_filename(self.temp_file_path)
        os.remove(self.temp_file_path)