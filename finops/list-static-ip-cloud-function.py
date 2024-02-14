import os
from google.cloud import compute_v1

project = os.environ.get('GCP_PROJECT')

def list_unused_static_ips(request):
    """
    檢視並返回所有未使用的靜態 IP 地址。

    Args:
        request (flask.Request): 進入 Cloud Function 的請求物件。

    Returns:
        dict: 包含未使用的靜態 IP 地址資訊的字典，格式為 {'unused_static_ips': unused_ips}。
    """

    # 從環境變數中獲取要檢查的所有地區
    regions = get_all_regions()

    # 初始化 Compute 客戶端
    compute_client = compute_v1.AddressesClient()

    unused_ips = []

    # 遍歷所有地區
    for region in regions:
        # 檢索指定地區的 IP 地址
        addresses = compute_client.list(project=project, region=region)

        # 遍歷地區中的 IP 地址
        for address in addresses:
            # 檢索每個 IP 地址的屬性
            address_details = {
                'address': address.address,
                'type': address.address_type,
                'region': region
            }

            # 如果地址未使用，則將其資訊添加到列表中
            if address.status == 'RESERVED':
                unused_ips.append(address_details)

    # 返回所有未使用的靜態 IP 地址資訊
    return {'unused_static_ips': unused_ips}

def get_all_regions():
    """
    檢索並返回所有可用地區的名稱。

    Returns:
        list: 包含所有可用地區名稱的列表。
    """

    # 初始化 Regions 客戶端
    region_client = compute_v1.RegionsClient()

    # 獲取所有地區的名稱
    regions = []
    for region in region_client.list(project=project):
        regions.append(region.name.split('/')[-1])
    return regions