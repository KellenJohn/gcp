import os
import logging
import datetime
import googleapiclient
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from google.auth import compute_engine

# initialize global
compute = googleapiclient.discovery.build('compute', 'v1')
# credentials = GoogleCredentials.get_application_default()

def delete_unattached_pds(project_id):
    logging.getLogger().setLevel(logging.INFO)
    logging.info("開始檢查 Disk")
    # get list of disks and iterate through it:
    disksRequest = compute.disks().aggregatedList(project=project_id)
    orphaned_disks = []
    total_size_gb = 0
    
    while disksRequest is not None:
        diskResponse = disksRequest.execute()
        for name, disks_scoped_list in diskResponse['items'].items():
            # 這個方法用於從字典中獲取指定鍵的值, 如果指定鍵 'warning' 不存在於字典中是我們要查的資料
            if disks_scoped_list.get('warning') is None: 
                for disk in disks_scoped_list['disks']:  # iterate through disks              
                    if disk.get('users') is None:
                        diskName = disk['name']
                        diskSize = int(disk['sizeGb'])                
                        diskZone = str((disk['zone'])).rsplit('/',1)[1]
                        diskAttachTime = disk.get('lastAttachTimestamp')
                        diskInfo = {
                                    'diskName': diskName, 
                                    'status': 'Unused Disk', 
                                    'AttachTime': diskAttachTime, 
                                    'diskZone': diskZone, 
                                    'sizeGb': diskSize
                                    }
                        orphaned_disks.append(diskInfo)
                        total_size_gb += diskSize

        disksRequest = compute.disks().aggregatedList_next(previous_request=disksRequest, previous_response=diskResponse)
       
    if orphaned_disks:
        return {'unused_disk': orphaned_disks, 'total_size_gb': total_size_gb}

    return {'total_size_gb': total_size_gb}
    

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
                print('-----------------------------------------------------------')
                continue

            # 調用 list_unused_static_ips 函數並傳入專案 ID
            result = delete_unattached_pds(project['projectId'])
        
            if not result.get('unused_disk'):
                print("健康")
                print('-----------------------------------------------------------')
            else:
                num_unhealthy_disks = len(result['unused_disk'])
                total_size_gb = result['total_size_gb']
                print(f"請檢查，找到有 {num_unhealthy_disks} 個 Disk 閒置資源，總 sizeGb 為 {total_size_gb} Gb")
                print('-----------------------------------------------------------')
     
    except Exception as e:
        print(f"An error occurred: {str(e)}")
 

if __name__ == '__main__':
    list_projects()