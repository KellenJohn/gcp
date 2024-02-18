import logging
import os
import datetime
import dateutil.parser
import googleapiclient
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from datetime import datetime
from basicauth import decode


# initialize global
compute = googleapiclient.discovery.build('compute', 'v1')
credentials = GoogleCredentials.get_application_default()
project = os.environ.get('GCP_PROJECT')

def delete_unattached_pds(request):
    logging.getLogger().setLevel(logging.INFO)
    logging.info("開始檢查 Disk")
    # get list of disks and iterate through it:
    disksRequest = compute.disks().aggregatedList(project=project)
    orphaned_disks = []
    while disksRequest is not None:
        diskResponse = disksRequest.execute()
        for name, disks_scoped_list in diskResponse['items'].items():
            if disks_scoped_list.get('warning') is None:
                for disk in disks_scoped_list['disks']: # iterate through disks
                    logging.info(disk)              
                    if disk.get('users') is None:
                        diskName = disk['name']
                        diskSize = disk['sizeGb']                
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

        disksRequest = compute.disks().aggregatedList_next(previous_request=disksRequest, previous_response=diskResponse)
    
    if orphaned_disks:
        return {'unused_disk': orphaned_disks}
    
    return "disk information logged"