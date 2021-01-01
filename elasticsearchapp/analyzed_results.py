import requests

article_id = "0c9795811a0c5e0127e542c3"
body_url = "http://127.0.0.1:9200/articles/_doc/" + article_id + "/_termvectors?fields=body"

payload = {}
headers = {}

response = requests.request("GET", body_url, headers=headers, data=payload)
response = response.json()

tokenized_body = response["term_vectors"]["body"]["terms"]

for token in tokenized_body:
    print(token)
