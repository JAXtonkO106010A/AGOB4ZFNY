import httplib, urllib, base64, json
from openpyxl import Workbook
from openpyxl import load_workbook
from azure.storage.table import TableService, Entity

# This program reads controls from Azure Table and use Azure KeyPhrases API to extract key phrases
# File with KeyPhrase API subscription key in json format
keyfile = 'Credential.json'
with open(keyfile,'r') as k:
    key = json.load(k)

# File with storage account (Azure Table) info in json format
keyfile = 'Table.json'
with open(keyfile,'r') as k:
    t = json.load(k)
    acc = t['acc']
    tkey = t['key']
    tab = t['tab']

table_service = TableService(account_name=acc, account_key=tkey)

# KeyPhrases API headers
headers = {
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': key['key'],
}
params = urllib.urlencode({
})

controls = table_service.query_entities('wwcccs', filter=None)

for control in controls:
    id = control.PartitionKey + '-' + control.RowKey
    text = control.ControlDescription
    body = json.dumps({
        "documents" : [
            {
                "id": id,
                "text": text,
            }
        ]
    })
    try:
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/text/analytics/v2.0/keyPhrases?%s" % params, body, headers)
        response = conn.getresponse()
        data = json.loads(response.read())
        documents = data['documents']
        kp = ", ".join(documents[0]['keyPhrases'])
        print(documents[0]['id']+": "+kp)
        updated_control = {'PartitionKey': control.PartitionKey, 'RowKey': control.RowKey, 'KeyPhrases': kp}
        table_service.insert_or_merge_entity('wwcccs', updated_control)
        conn.close()
    except Exception as e:
        print(id+": "+e.message+"\n"),response.status, response.reason, response.msg
