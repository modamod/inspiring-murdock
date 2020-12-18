'''
    This  lambda is a test lambda to read from kinesis stream
'''
import base64

def lambda_handler(event, context):

    records = event.get('Records')
    data = []
    for record in records:
        payload = base64.b64decode(record["kinesis"]["data"])
        data.append({
            'partition': record['kinesis']['partitionKey'],
            'data': payload
        })

    print(data)
    return data
