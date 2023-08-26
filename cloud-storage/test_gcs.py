import logging
from google.cloud import storage
from google.cloud.exceptions import NotFound, GoogleCloudError
import subprocess


def set_gcloud_project(project_id):
    command = ['gcloud', 'config', 'set', 'project', project_id]
    try:
        subprocess.run(command, check=True)
        print(f'Successfully set Google Cloud project to: {project_id}')
    except subprocess.CalledProcessError as e:
        print(f'Error setting Google Cloud project: {e}')

# 要設定的 Google Cloud 項目 ID
project_id = 'esun-cncf'

# 執行設定命令
set_gcloud_project(project_id)


class GCSTools:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.client = storage.Client()
        self.bucket = self.client.get_bucket(bucket_name)
        self.logger = logging.getLogger(__name__)

    def upload_file(self, local_file_path, remote_file_name):
        try:
            blob = self.bucket.blob(remote_file_name)
            blob.upload_from_filename(local_file_path)
            self.logger.info(f'File {local_file_path} uploaded to GCS bucket {self.bucket_name}.')
        except NotFound:
            self.logger.error(f'Bucket {self.bucket_name} not found.')
        except GoogleCloudError as e:
            self.logger.error(f'An error occurred: {e}')

# 設置日誌級別和格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 創建 GCSTools 實例，指定 GCS 存儲桶名稱
bucket_name = 'training-instance-group-template'
gcs_uploader = GCSTools(bucket_name)


# 調用 upload_file 方法上傳文件
local_file_path = 'local-file.txt'
remote_file_name = 'demo/remote-file.txt'
gcs_uploader.upload_file(local_file_path, remote_file_name)