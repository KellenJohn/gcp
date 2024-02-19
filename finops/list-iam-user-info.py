"""
GCP IAM Policy Extraction 工具

此工具用於從 Google Cloud Platform (GCP) 專案的 IAM Policy 中提取角色和成員資訊，並將其儲存為 CSV 檔案。

功能：
- 列出所有專案
- 提取每個專案的 IAM Policy 中的角色和成員資訊
- 將提取的資訊儲存為 CSV 檔案

使用方法：
1. 請確保已安裝 Google Cloud SDK 並完成驗證（使用 `gcloud auth login`）。
2. 執行此程式，將會自動列出所有專案及其 IAM Policy 資訊並將結果儲存為 CSV 檔案。

注意事項：
- 此程式需要使用者有足夠的權限來存取 GCP 專案的 IAM Policy。
- 請確保正確設定程式中的 `csv_file_path` 變數，以指定 CSV 檔案的儲存位置。
"""

import os
import json
import csv
from datetime import datetime
import googleapiclient.discovery
from google.auth import compute_engine

def list_projects():
    """
    列出所有專案資訊。

    Returns:
        list: 包含所有專案 ID 的列表。
    """
    # 依使用的此程式的帳號，創建一個認證的憑證
    credentials = compute_engine.Credentials()

    try:
        # 創建 Cloud Resource Manager 服務物件
        service = googleapiclient.discovery.build('cloudresourcemanager', 'v1', credentials=credentials)

        # 發起獲取專案列表的請求
        request = service.projects().list()
        response = request.execute()

        projects_data = []
        for project in response.get('projects', []):
            projects_data.append(project['projectId'])

        return projects_data
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return []

def extract_permissions(iam_policy, project_id, etl_time):
    """
    從提供的 IAM Policy 中提取角色和成員資訊。

    Args:
        iam_policy (dict): 包含 IAM Policy 資訊的字典。
        project_id (str): 專案 ID。
        etl_time (str): ETL（Extract, Transform, Load）執行時間的格式化字串（如 "%Y%m%d"）。

    Returns:
        list: 包含提取的角色和成員資訊的字典列表。
    """
    extracted_data = []

    for binding in iam_policy.get('bindings', []):
        role = binding.get('role')
        for member in binding.get('members', []):
            # 檢查成員類型：user(先以人員為主) 或 serviceAccount(暫先不要，排入之後 SA 的排程的工作再開發)
            if member.startswith("user:"):
                member_id = member.split(":")[-1]
                extracted_data.append({
                    "Project": project_id,
                    "Role": role,
                    "MemberType": "user",
                    "MemberID": member_id,
                    "ETLTime": etl_time
                })

    return extracted_data

def main():
    """
    主函式，用於執行程式的主要邏輯。此函式將列出所有專案的 IAM Policy，提取角色和成員資訊，並將其儲存為 CSV 檔案。

    Returns:
        None
    """
    project_ids = list_projects()

    credentials = compute_engine.Credentials()
    service = googleapiclient.discovery.build('cloudresourcemanager', 'v1', credentials=credentials)

    all_data = []

    for project_id in project_ids:
        response = service.projects().getIamPolicy(resource=project_id, body={}).execute()
        iam_policy = response

        etl_time = datetime.now().strftime("%Y%m%d")

        # 提取 IAM Policy 中的角色和成員資訊
        extracted_data = extract_permissions(iam_policy, project_id, etl_time)

        # 將本次專案的資料加入總列表中
        all_data.extend(extracted_data)

    # 寫入 CSV 檔案
    csv_file_path = "output.csv"
    csv_columns = ["Project", "Role", "MemberType", "MemberID", "ETLTime"]

    with open(csv_file_path, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
        writer.writeheader()
        writer.writerows(all_data)

    print("CSV 文件已生成:", csv_file_path)

if __name__ == "__main__":
    main()