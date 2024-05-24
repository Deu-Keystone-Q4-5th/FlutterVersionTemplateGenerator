import json

import requests

class


request_link = f"https://www.aladin.co.kr/ttb/api/ItemList.aspx?ttbkey={key}&QueryType=ItemNewAll&MaxResults=10&start=1&SearchTarget=Book&output=js&Version=20131101"
response = requests.get(request_link)
text = response.text
response.json()
print(response.json())
