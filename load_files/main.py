import json
from google.cloud import bigquery


def load_files(request):
    """Loads CSV files with `processing` prefix from Cloud Storage bucket to
    BigQuery table. Creates a new table called `history` if table doesn't
    exist. Expects a Cloud Storage bukcet name and BigQuery dataset name in
    the request json."""
    request_json = request.get_json()

    if "bucket" and "dataset" and "names" in request_json:
        bucket = request_json["bucket"]
        dataset = request_json["dataset"]
        object_names = request_json["names"]
    else:
        raise Exception("Bucket name and/or dataset name and/or file list is missing.")

    table_id = f"{dataset}.history"

    client = bigquery.Client()

    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("vehicle_id", "STRING"),
            bigquery.SchemaField("date", "DATE"),
            bigquery.SchemaField("hour", "INT64"),
            bigquery.SchemaField("minute", "INT64"),
            bigquery.SchemaField("latitude", "FLOAT64"),
            bigquery.SchemaField("longitude", "FLOAT64"),
            bigquery.SchemaField("tire_pressure", "FLOAT64"),
            bigquery.SchemaField("speed", "FLOAT64"),
            bigquery.SchemaField("temperature", "FLOAT64"),
            bigquery.SchemaField("gas_composition", "STRING"),
        ],
        skip_leading_rows=1,
        source_format=bigquery.SourceFormat.CSV,
    )

    for name in object_names:
        uri = f"gs://{bucket}/processing/{name}"
        load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)
        load_job.result()
