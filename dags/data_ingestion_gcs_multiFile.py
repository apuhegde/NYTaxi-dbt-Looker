import os
import logging
from datetime import datetime

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import pyarrow.csv as pv
import pyarrow.parquet as pq
from google.cloud import storage
#from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator

#set up logging
logger = logging.getLogger(__name__)

path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
yellow_url_prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
yellow_url_template = yellow_url_prefix + 'yellow_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.csv.gz'
yellow_output_template = path_to_local_home + '/yellow_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.csv.gz'
# yellow_file_url = f'{yellow_url_prefix}/{yellow_file_template}'
# dataset_file = "yellow_tripdata_2021-01.csv.gz"
# dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/{dataset_file}"
parquet_file = path_to_local_home + '/yellow_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.parquet'
yellow_gcs_path_template = 'raw/yellow_tripdata/{{ execution_date.strftime(\'%Y\') }}/yellow_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.parquet'

logger.info(f'Dataset url is {yellow_url_template}, local_home is {path_to_local_home}, parquet file is {parquet_file}')

#GCP environment variables
BUCKET=os.environ.get("GCP_GCS_BUCKET")
#PROJECT_ID=os.environ.get("GCP_PROJECT_ID")
#PROJECT_NAME=os.environ.get("GOOGLE_CLOUD_PROJECT")
#BIGQUERY_DATASET=os.environ.get("BIGQUERY_DATASET", 'trips_data_all')

logger.info(f'{BUCKET} is the bucket.')

#set default args for the dag
default_args = {
    "owner": "admin",
    "depends_on_past": False,
    "retries": 1,
}


def format_to_parquet(src_file, dest_file):
    if not (src_file.endswith('.csv') or src_file.endswith('.csv.gz')):
        logger.error("Can only accept source files in CSV format, for the moment")
        return
    table = pv.read_csv(src_file)
    pq.write_table(table, dest_file)


def upload_to_gcs(bucket, object_name, local_file):
    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    :param bucket: GCS bucket name
    :param object_name: target path & file-name
    :param local_file: source path & file-name
    :return:
    """
    # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # (Ref: https://github.com/googleapis/python-storage/issues/74)
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
    # End of Workaround

    client = storage.Client()
    #bucket = client.bucket(bucket)
    bucket = client.get_bucket(bucket)

    blob = bucket.blob(object_name)
    logger.info(f'Blob is {blob}')
    blob.upload_from_filename(local_file)



with DAG(dag_id="yellow_taxi_gcs_dag",
         start_date=datetime(2019,1,1),
         schedule_interval="0 6 2 * *",
         default_args=default_args,
         catchup=True,
         max_active_runs=3,
         tags=['dtc-de']) as yellow_taxi_gcs:
    
    download_dataset_task = BashOperator(
        task_id="download_dataset_task",
        bash_command=f"curl -sSLf {yellow_url_template} > {yellow_output_template}"
    )

    format_to_parquet_task = PythonOperator(
        task_id="format_to_parquet_task",
        python_callable=format_to_parquet,
        op_kwargs={
            "src_file": yellow_output_template,
            "dest_file": parquet_file
        }
    )

    local_to_gcs_task = PythonOperator(
        task_id="local_to_gcs_task",
        python_callable=upload_to_gcs,
        op_kwargs={
            "bucket": BUCKET,
            "object_name": yellow_gcs_path_template,
            "local_file": parquet_file
        }
    )

    purge_task = BashOperator(
        task_id="purge_task",
        bash_command=f"rm {yellow_output_template} {parquet_file}"
    )
download_dataset_task >> format_to_parquet_task >> local_to_gcs_task >> purge_task