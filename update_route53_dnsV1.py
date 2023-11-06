import boto3
import os

# Initialize a Route53 client
client = boto3.client('route53')

# Get the hosted zone ID from the environment variable
hosted_zone_id = os.environ.get('Z04395233QIU1MNFUZO2')

def get_record_values(record_name, record_type):
    """Retrieve the values for a specific DNS record."""
    response = client.list_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        StartRecordName=record_name,
        StartRecordType=record_type,
        MaxItems='1'
    )

    for record_set in response['ResourceRecordSets']:
        if record_set['Name'].rstrip('.') == record_name and record_set['Type'] == record_type:
            return [record['Value'] for record in record_set['ResourceRecords']]

    raise Exception(f"Record {record_name} not found.")

def change_dns_record(action, record_name, record_type, record_values):
    """Create, update, or delete a DNS record."""
    change_batch = {
        'Changes': [
            {
                'Action': action,
                'ResourceRecordSet': {
                    'Name': record_name,
                    'Type': record_type,
                    'TTL': 300,
                    'ResourceRecords': [{'Value': value} for value in record_values]
                }
            }
        ]
    }

    response = client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch=change_batch
    )
    return response['ChangeInfo']

# Use environment variables for source and destination, and record type
source_record_name = os.environ.get('SOURCE_RECORD_NAME')
destination_record_name = os.environ.get('DESTINATION_RECORD_NAME')
record_type = os.environ.get('RECORD_TYPE')

if source_record_name and destination_record_name and record_type:
    try:
        # Get the value(s) of the source record
        source_values = get_record_values(source_record_name, record_type)

        # Update the destination record with the source's value(s)
        print(f"Updating {destination_record_name} with the value(s) from {source_record_name}...")
        change_dns_record('UPSERT', destination_record_name, record_type, source_values)
        print(f"{destination_record_name} has been updated with the value(s) from {source_record_name}.")

        # Optionally, delete the source record
        # Uncomment the following lines if you want to delete the source record after updating
        print(f"Deleting {source_record_name}...")
        change_dns_record('DELETE', source_record_name, record_type, source_values)
        print(f"{source_record_name} has been deleted.")

    except Exception as e:
        print(f"An error occurred: {e}")
else:
    print("SOURCE_RECORD_NAME, DESTINATION_RECORD_NAME, and RECORD_TYPE environment variables are required.")
