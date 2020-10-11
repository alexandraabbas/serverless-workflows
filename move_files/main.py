import json
from google.cloud import storage


def move_files(request):
    """Given a bucket, object names, source and destination prefixes
    it renames each object at source  with a new destination prefix.
    Note, this function doesn't move objects accross buckets only
    within a bucket."""
    request_json = request.get_json()
    bucket_name = request_json["bucket"]
    object_names = request_json["names"]
    source = request_json["source"]
    destination = request_json["destination"]

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    for name in object_names:
        source_blob = bucket.blob(f"{source}/{name}")
        bucket.rename_blob(source_blob, f"{destination}/{name}")
