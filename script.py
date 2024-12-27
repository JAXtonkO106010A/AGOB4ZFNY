import requests
import json
import datetime


def fetch_data():
    # 从接口获取数据
    token = requests.get("https://v2.jinrishici.com/token").json().get("data")
    headers = {
       "X-User-Token":token
    }
    url = 'https://v2.jinrishici.com/sentence'
    response = requests.get(url,headers=headers)
    data = response.json()
    return data


def append_to_readme(data):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('README.md', 'a', encoding='utf-8') as file:
        file.write(f"\n\n{timestamp}\n")
        file.write(f"## {data['data']['origin']['title']}\n")
        file.write(f"{data['data']['content']}\n")


if __name__ == "__main__":
    data = fetch_data()
    append_to_readme(data)
