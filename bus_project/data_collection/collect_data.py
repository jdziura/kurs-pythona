import os
import requests
import json

from dotenv import load_dotenv

load_dotenv()

def list_of_key_values_to_dict(list_of_values):
    return {item['key']: item['value'] for item in list_of_values}

def fetch_and_store_data(file_path):
    api_key = os.environ.get("API_KEY")
    if api_key is None:
        raise ValueError("API_KEY is not set")
    
    id = "ab75c33d-3a26-4342-b36a-6e5fef0a3ac3"
    url = f"https://api.um.warszawa.pl/api/action/dbstore_get/?id={id}&apikey={api_key}"

    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Request failed with status code {response.status_code}")
    
    data = response.json()

    with open(file_path, 'w') as f:
        json.dump(data, f)

def main():
    data_file_path = os.path.join('data', 'bus_stops_data.json')

    if not os.path.exists(data_file_path):
        os.makedirs('data', exist_ok=True)
        fetch_and_store_data(data_file_path)

    with open(data_file_path, 'r') as f:
        data = json.load(f)
        data = data['result']
        data = [list_of_key_values_to_dict(item['values']) for item in data]
        for i in range(30):
            print(data[-i])

if __name__ == "__main__":
    main()