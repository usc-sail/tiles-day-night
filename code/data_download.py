import boto3
import botocore
from pathlib import Path
import os


def create_folder(save_path):
    if Path.exists(save_path) is False: Path.mkdir(save_path)


def download_data(save_root_path, download_bucket, prefix=''):
    # Create the local saved folder
    if Path.exists(save_root_path) is False: Path.mkdir(save_root_path)

    # Download data from bucket
    for object_summary in download_bucket.objects.filter(Prefix=prefix):
        if len(object_summary.key.split('/')) != 0:
            save_sub_path = save_root_path
            for i in range(len(object_summary.key.split('/'))-1):
                save_sub_path = save_sub_path.joinpath(object_summary.key.split('/')[i])
                create_folder(save_sub_path)

        # if Path.exists(save_root_path.joinpath(object_summary.key)) is True:
        #    print("Data already downloaded: " + object_summary.key)
        #    continue

        print("Download data: " + object_summary.key)
        try:
            os.system('aws s3 cp s3://' + download_bucket.name + '/' + object_summary.key + ' ' + str(save_root_path.joinpath(object_summary.key)))
            # download_bucket.download_file(object_summary.key, str(save_root_path.joinpath(object_summary.key)))
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise


if __name__ == '__main__':

    s3 = boto3.resource('s3')

    # bucket_str = 'tiles-phase1-opendataset'
    bucket_str = 'tiles-phase1-wav123-processed'
    opendataset_bucket = s3.Bucket(bucket_str)

    save_root_path = Path(__file__).parent.absolute().parents[0].joinpath('data')
    create_folder(save_root_path)
    download_data(save_root_path.joinpath(bucket_str), opendataset_bucket, prefix='3_preprocessed_data')
    download_data(save_root_path.joinpath(bucket_str), opendataset_bucket, prefix='survey')
    download_data(save_root_path.joinpath(bucket_str), opendataset_bucket, prefix='metadata')
    download_data(save_root_path.joinpath(bucket_str), opendataset_bucket, prefix='realizd')
    download_data(save_root_path.joinpath(bucket_str), opendataset_bucket, prefix='omsignal')
