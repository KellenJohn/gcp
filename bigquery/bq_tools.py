import pandas as pd
from google.api_core.exceptions import GoogleAPICallError, BadRequest, NotFound
from google.cloud import bigquery, bigquery_storage, storage

class BQDataFetcher:
    def __init__(self, project, dataset, table):
        self.project = project
        self.dataset = dataset
        self.table = table
        self.bqclient = bigquery.Client(project=project)


    def fetch_table_dataframe(self, query_string, limit=None):
        """
        初始化 BQDataFetcher 物件。

        Args:
            project (str): Google Cloud 專案 ID。
            dataset (str): BigQuery 資料集名稱。
            table (str): BigQuery 表格名稱。
        
        Memo:
            Big Query URI - bq://project_id.dataset.table
            不適用於取用大資料，Dataframe 型別會以最大 type 引入，例如 float64 需另處理！

        """
        try:
            if limit is not None:
                query_string += f" LIMIT {limit}"
            query_job = self.bqclient.query(query_string)
            query_job_result = query_job.result()
            df = query_job_result.to_dataframe()
            return df
        
        except NotFound:
            raise Exception('The specified table does not exist in BigQuery.')
                            
        except (GoogleAPICallError, BadRequest) as e:
            # BigQuery API 調用錯誤和請求錯誤
            raise Exception(f'Error fetching data from BigQuery: {str(e)}')
                            
        except Exception as e:
            raise Exception(f'An unexpected error occurred: {str(e)}')
                            
            
    def insert_dataframe_to_bq(self, dataframe, destination_table_id, write_disposition='WRITE_TRUNCATE', source_format='CSV', schema=None):
        """
        從 BigQuery 表格中檢索資料並返回 DataFrame。

        Args:
            query_string (str): BigQuery SQL 查詢字符串。
            limit (int, optional): 限制結果筆數。默認為 None 即不限制。

        Returns:
            pandas.DataFrame: 包含查詢結果的 DataFrame。

        Raises:
            Exception: 如果發生任何錯誤，將引發異常。

        """
        try:
            # 指定目標表格
            dataset_ref = self.bqclient.dataset(self.dataset)
            table_ref = dataset_ref.table(destination_table_id)

            # 将 DataFrame 插入到 BigQuery 表格
            job_config = bigquery.LoadJobConfig()
            job_config.write_disposition = write_disposition
            job_config.source_format = source_format

            if schema is not None:
                job_config.schema = schema

            # 将 DataFrame 加载到 BigQuery 表格
            job = self.bqclient.load_table_from_dataframe(dataframe, table_ref, job_config=job_config)

            # 等待加载作業完成
            job.result()

            print(f'DataFrame load successfuly {self.dataset}.{destination_table_id}')

        except (GoogleAPICallError, BadRequest) as e:
            raise Exception(f'Error inserting data into BigQuery: {str(e)}')    