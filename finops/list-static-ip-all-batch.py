import os
from google.cloud import compute_v1
from google.auth import compute_engine
from googleapiclient import discovery

def list_unused_static_ips(project_id):
    """
    返回未使用的靜態 IP 地址資訊。

    Args:
        project_id (str): 專案 ID。

    Returns:
        dict: 包含未使用的靜態 IP 地址資訊的字典。
    """
    try:
        # 初始化 Compute Client
        compute_client = compute_v1.AddressesClient()

        unused_ips = []

        # 獲取取所有地區列表
        regions = get_all_regions(project_id)

        # 遍歷所有地區
        for region in regions:
            # 檢索指定地區的 IP 地址
            addresses = compute_client.list(project=project_id, region=region)

            # 遍歷地區中的 IP 地址
            for address in addresses:
                # 檢查 IP 地址是否未使用
                if address.status == 'RESERVED':
                    address_details = {
                        'address': address.address,
                        'type': address.address_type,
                        'region': region
                    }
                    unused_ips.append(address_details)

        # 返回所有未使用的静態 IP 地址資訊
        return {'unused_ips(with external & internal)': unused_ips}

    except Exception as e:
        return {'error': str(e)}

def get_all_regions(project_id):
    """
    返回指定專案的所有地區名稱列表。

    Args:
        project_id (str): 專案 ID。

    Returns:
        list: 地區名稱列表。
    """
    # 初始化 Regions Client
    region_client = compute_v1.RegionsClient()

    # 獲取所有地區的名稱
    regions = []
    for region in region_client.list(project=project_id):
        regions.append(region.name.split('/')[-1])
    return regions

def list_projects():
    """
    列出所有專案及其未使用的靜態 IP 地址資訊。
    """
    # 依使用的此程式的帳號，創建一個認證的憑證
    credentials = compute_engine.Credentials()

    try:
        # 創建 Cloud Resource Manager 服務物件
        service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)

        # 發起獲取專案列表的請求
        request = service.projects().list()
        response = request.execute()

        # 印出專案資訊
        print('{:<20} {:<22} {:<21}'.format('PROJECT_ID', 'NAME', 'PROJECT_NUMBER'))
        for project in response.get('projects', []):
            print('{:<20} {:<22} {:<21}'.format(project['projectId'], project['name'], project['projectNumber']))

            # 檢查 Compute Engine API 是否已啟用
            if not is_compute_engine_api_enabled(project['projectId']):
                print("Compute Engine API is not enabled for this project.")
                continue

            # 調用 list_unused_static_ips 函數並傳入專案 ID
            result = list_unused_static_ips(project['projectId'])
            if 'error' in result:
                print("An error occurred:", result['error'])
            else:
                print(result)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

def is_compute_engine_api_enabled(project_id):
    """
    檢查指定專案的 Compute Engine API 是否已啟用。

    Args:
        project_id (str): 專案 ID。

    Returns:
        bool: 如果 Compute Engine API 已啟用則返回 True，否則返回 False。
    """
    # 依使用的此程式的帳號，創建一個認證的憑證
    credentials = compute_engine.Credentials()

    # 創建服務物件
    service = discovery.build('serviceusage', 'v1', credentials=credentials)

    # 發起請求檢查 Compute Engine API 是否已啟用
    request = service.services().get(name=f'projects/{project_id}/services/compute.googleapis.com')
    response = request.execute()

    return response['state'] == 'ENABLED'

# 調用函數来列出專案
if __name__ == '__main__':
    list_projects()