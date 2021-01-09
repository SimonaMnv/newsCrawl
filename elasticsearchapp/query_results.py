import requests


def get_all_ids():
    body_url = "http://127.0.0.1:9200/articles/_search?size=10000"

    all_ids = []
    payload = {}
    headers = {}

    response = requests.request("GET", body_url, headers=headers, data=payload)
    response = response.json()

    length = response["hits"]["total"]["value"]

    for i in range(0, length):
        all_ids.append(response["hits"]["hits"][i]["_id"])

    return all_ids


def analyzed_results_body():
    all_ids = get_all_ids()
    tokenized_body_results = []
    final_body = []

    for article_id in all_ids:
        body_url = "http://127.0.0.1:9200/articles/_doc/" + str(article_id) + "/_termvectors?fields=body"

        payload = {}
        headers = {}

        response = requests.request("GET", body_url, headers=headers, data=payload)
        response = response.json()

        if len(response["term_vectors"]) > 0:
            tokenized_body = response["term_vectors"]["body"]["terms"]
        else:
            tokenized_body = ""

        [tokenized_body_results.append(token) for token in tokenized_body]
        final_body.append(tokenized_body_results)
        tokenized_body_results = []

    return final_body


def analyzed_results_title():
    all_ids = get_all_ids()
    tokenized_title_results = []
    final_title = []

    for article_id in all_ids:
        body_url = "http://127.0.0.1:9200/articles/_doc/" + str(article_id) + "/_termvectors?fields=title"

        payload = {}
        headers = {}

        response = requests.request("GET", body_url, headers=headers, data=payload)
        response = response.json()

        tokenized_title = response["term_vectors"]["title"]["terms"]

        [tokenized_title_results.append(token) for token in tokenized_title]
        final_title.append(tokenized_title_results)
        tokenized_title_results = []

    return final_title


def analyzed_results_tags():
    all_ids = get_all_ids()
    tokenized_tags_results = []
    final_tags = []

    for article_id in all_ids:
        body_url = "http://127.0.0.1:9200/articles/_doc/" + str(article_id) + "/_termvectors?fields=tags"

        payload = {}
        headers = {}

        response = requests.request("GET", body_url, headers=headers, data=payload)
        response = response.json()

        if len(response["term_vectors"]) > 0:
            tokenized_tags = response["term_vectors"]["tags"]["terms"]
        else:
            tokenized_tags = ""

        [tokenized_tags_results.append(token) for token in tokenized_tags]
        final_tags.append(tokenized_tags_results)
        tokenized_tags_results = []

    return final_tags


def get_categories(type):
    import requests
    murder = []
    drugs = []
    theft = []
    sex_crime = []
    terrorism = []
    other_crime = []

    url = "http://127.0.0.1:9200/articles/_search"

    if type == "murder":
        payload = "{\r\n  \"size\": 10000,\r\n  \"query\": {\r\n    \"term\": {\r\n      \"type\": {\r\n        " \
                  "\"value\": \"δολοφονια\"\r\n      }\r\n    }\r\n  }, \r\n  \"aggregations\": {\r\n    \"NAME\": {" \
                  "\r\n  " \
                  "    \"significant_text\": {\r\n        \"field\": \"type\"\r\n      }\r\n    }\r\n  }\r\n} "
        headers = {
            'Content-Type': 'application/json'
        }

    response = requests.request("GET", url, headers=headers, data=payload.encode('utf8'))
    response = response.json()
    length = response["hits"]["total"]["value"]

    for i in range(0, length):
        murder.append(response["hits"]["hits"][i]["_source"]["title"])

    return murder
