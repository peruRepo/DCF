import requests
from datetime import datetime, timedelta


def document_needs_update(db_url, doc_id):
    # Query CouchDB for the document
    response = requests.get(f"{db_url}{doc_id}",
                            auth=('admin', 'admin'))

    if response.status_code == 404:
        # Document does not exist
        return True

    document = response.json()
    last_updated = datetime.fromisoformat(document.get('last_updated'))
    if datetime.utcnow() - last_updated > timedelta(days=30):
        # Document was last updated more than a month ago
        return True

    # Document exists and was updated less than a month ago
    return False


def update_document(db_url, doc_id, data):
    # Insert or update the document in CouchDB
    response = requests.put(f"{db_url}{doc_id}", json=data,
                            auth=('admin', 'admin'))
    return response.json()


# Main
db_url = "http://localhost:5984/financial_statement/"
doc_id = "CIK0000320193"  # Document ID, e.g., based on CIK
api_url = "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json"

if document_needs_update(db_url, doc_id):
    # Fetch data from API
    headers = {'User-Agent': "email@address.com"}
    api_response = requests.get(api_url, headers=headers)
    data = api_response.json()
    data['last_updated'] = datetime.utcnow().isoformat()

    # Update document in CouchDB
    update_response = update_document(db_url, doc_id, data)
    print("Document updated:", update_response)
else:
    print("No update needed.")
