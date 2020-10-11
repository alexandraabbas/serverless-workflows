import json
from flask import jsonify
from google.cloud import storage


def remove_prefix(prefixed_names, prefix):
    clean_names = []
    for name in prefixed_names:
        if name != prefix:
            clean_names.append(name.replace(prefix, ""))

    return clean_names


def list_files(request):
    """Lists file names in a bucket. Expects a bucket name and optional prefix
    in the request json. Returns a list of file names without prefixes."""
    request_json = request.get_json()

    if request_json["bucket"]:
        bucket_name = request_json["bucket"]
    else:
        raise Exception("Bucket name is missing.")

    prefix = None

    if request_json["prefix"]:
        prefix = request_json["prefix"]

    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix, delimiter="/")

    names = [blob.name for blob in blobs]

    if prefix:
        names = remove_prefix(names, prefix)

    output = {"objects": names}

    return jsonify(output)
