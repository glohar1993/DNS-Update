# update_route53_dns.py
import boto3
import os

# Initialize a Route53 client
client = boto3.client('route53')

# Provide your hosted zone ID here
hosted_zone_id = 'YOUR_HOSTED_ZONE_ID'  # Replace with your actual hosted zone ID

def get_record_value(record_name, record_type='CNAME'):
    """Retrieve the value for a specific DNS record."""
    response = client.list_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        StartRecordName=record_name,
        StartRecordType=record_type,
        MaxItems='1'
    )
    
    for record_set in response['ResourceRecordSets']:
        if record_set['Name'].rstrip('.') == record_name and record_set['Type'] == record_type:
            return record_set['ResourceRecords'][0]['Value']
    
    raise Exception(f"Record {record_name} not found.")

def change_cname_record(action, record_name, record_value=None):
    """Create, update, or delete a CNAME record."""
    change_batch = {
        'Changes': [
            {
                'Action': action,
                'ResourceRecordSet': {
                    'Name': record_name,
                    'Type': 'CNAME',
                    'TTL': 300,
                }
            }
        ]
    }
    if action in ['CREATE', 'UPSERT']:
        change_batch['Changes'][0]['ResourceRecordSet']['ResourceRecords'] = [{'Value': record_value}]
    elif action == 'DELETE':
        # No need to set Value for DELETE action, but it needs to match the existing record
        change_batch['Changes'][0]['ResourceRecordSet']['ResourceRecords'] = [{'Value': record_value}]

    response = client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch=change_batch
    )
    return response['ChangeInfo']

# Use environment variables for source and destination
source_cname = os.environ.get('SOURCE_CNAME')
destination_cname = os.environ.get('DESTINATION_CNAME')

if source_cname and destination_cname:
    try:
        # Get the value of the source CNAME record
        source_value = get_record_value(source_cname)

        # Update the destination CNAME record with the source's value
        print(f"Updating {destination_cname} to have the value of {source_cname}...")
        change_cname_record('UPSERT', destination_cname, source_value)
        print(f"{destination_cname} has been updated with the value from {source_cname}.")

        # Delete the source CNAME record
        print(f"Deleting {source_cname}...")
        change_cname_record('DELETE', source_cname, source_value)
        print(f"{source_cname} has been deleted.")

    except Exception as e:
        print(f"An error occurred: {e}")
else:
    print("SOURCE_CNAME and DESTINATION_CNAME environment variables are required.")
