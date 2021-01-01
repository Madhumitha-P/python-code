import requests
import json
import jsonpath
from textwrap import indent

def test_first_case():
    entry_page = requests.get("https://reqres.in/api/users?page=2")
    print(entry_page)
    print(entry_page.status_code)
    print(entry_page.headers['Content-Type'])
#     json_response = json.loads(entry_page.text)
#     print(json_response)
#     text = jsonpath.jsonpath(json_response, 'data')
#     print(text[0])
#     for val in text[0]:
#         print(val)
    json_response = json.dumps(entry_page.json(),indent=4)
    print(json_response)

if __name__ == "__main__":
    test_first_case()
