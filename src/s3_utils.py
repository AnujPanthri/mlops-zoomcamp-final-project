import os
import re
import shutil


def s3_path_to_bucket_folder(s3_path):
    match = re.search(
        r"s3://([^/]+)/",
        s3_path,
    )
    # print(match.end())
    bucket_name, s3_folder = s3_path[5 : match.end() - 1], s3_path[match.end() :]
    # print(bucket_name, s3_folder)
    return bucket_name, s3_folder


def download_s3_folder(s3_resource, s3_path, local_dir):
    bucket_name, s3_folder = s3_path_to_bucket_folder(s3_path)
    if os.path.exists(local_dir):
        shutil.rmtree(local_dir)
    bucket = s3_resource.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=s3_folder):
        target = os.path.join(local_dir, os.path.relpath(obj.key, s3_folder))
        # print(target)
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))
        if obj.key[-1] == '/':
            continue
        bucket.download_file(obj.key, target)
