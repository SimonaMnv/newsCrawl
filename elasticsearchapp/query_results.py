import requests
import re
import json


# for dependency analyze
def gather_raw_verbs(type, threshold):
    url = "http://127.0.0.1:9200/articles/_search"
    keyword = []

    payload = "{\r\n  \"size\":0, \r\n  \"query\": {\r\n    \"match\": {\r\n      \"type\": \"" + type + "\"\r\n   " \
             " }\r\n " \
             " },\r\n  \"aggregations\":{\r\n    \"NAME\":{\r\n      \"significant_text\": {\r\n       " \
             " \"field\": \"body.simple_analyzer\",\r\n        \"size\": " + str(
        threshold) + "\r\n      }\r\n   " \
                     " }\r\n  }\r\n}"
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload.encode("utf8"))
    response = response.json()

    for i in range(0, threshold):
        keyword.append([re.sub("σ$", "ς", response['aggregations']['NAME']['buckets'][i]['key'])])

    print("elastic keywords:", keyword)

    return keyword


# for dependency analyze testing
def get_latest_raw_data(article_index=0, article_type='δολοφονια'):
    url = "http://127.0.0.1:9200/articles/_search"
    raw_data = []
    raw_type = []

    payload = "{\r\n  \"track_total_hits\": true, \r\n    \"size\": 1000,\r\n    \"query\": {\r\n        " \
              "\"term\": {\r\n            \"type\": {\r\n                \"value\": \"" + article_type + "\"\r\n         " \
             "   }\r\n        }\r\n    }\r\n}"

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload.encode("utf8"))
    response = response.json()

    article_body = response["hits"]["hits"][article_index]["_source"]["body"] + " " + \
                   response["hits"]["hits"][article_index]["_source"]["title"] + " "
    raw_data.append([article_body])
    raw_type.append(response["hits"]["hits"][article_index]["_source"]["type"])

    return raw_data, raw_type


# for dash data
def get_n_raw_data(crime_type, from_date, to_date, threshold=20):  # TODO: change threshold after caching
    url = "http://127.0.0.1:9200/articles/_search"
    total_n_data = []

    payload = json.dumps({
        "size": threshold,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "type": crime_type
                        }
                    },
                    {
                        "match": {
                            "scope": "ΕΛΛΑΔΑ"
                        }
                    },
                    {
                        "range": {
                            "date": {
                                "gte": from_date,
                                "lte": to_date
                            }
                        }
                    }
                ]
            }
        }
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload.encode("utf8"))
    response = response.json()

    for datum in response['hits']['hits']:
        data = {
            "Date": datum['_source']['date'],
            "Title": datum['_source']['title'],
            "Body": datum['_source']['body'],
            "Type": datum['_source']['type'],
            "Tags": datum['_source']['tags'],
            "Victim": datum['_source']['crime_analysis']['victim_gender'],
            "Criminal Status": datum['_source']['crime_analysis']['criminal_status'],
            "Acts": datum['_source']['crime_analysis']['acts_committed'],
            "Locations": datum['_source']['crime_analysis']['location_of_crime'],
            "Ages": datum['_source']['crime_analysis']['ages_involved'],
            "Time of Crime": datum['_source']['crime_analysis']['time_of_crime'],
            "Drug": datum['_source']['crime_analysis']['drug_type'],
            "Link": "Click for Link"
        }
        total_n_data.append(data)

    return total_n_data


def get_all_raw_data():
    url = "http://127.0.0.1:9200/articles/_search"
    raw_data = []
    raw_type = []

    payload = "{\r\n  \"track_total_hits\": true, \r\n  \"size\":20000\r\n\r\n}"
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    response = response.json()

    length = response["hits"]["total"]["value"]
    print("length of data", length)

    for i in range(0, length):
        article_body = response["hits"]["hits"][i]["_source"]["body"] + " " + \
                       response["hits"]["hits"][i]["_source"]["title"] + " " + \
                       response["hits"]["hits"][i]["_source"]["tags"] + " "
        raw_data.append([article_body])
        raw_type.append(response["hits"]["hits"][i]["_source"]["type"])

    return raw_data, raw_type


def get_all_analyzed_data():
    raw_data, raw_type = get_all_raw_data()  # todo: index analyzed without raw data func
    tokenized_data = []
    tokenized_total = []

    url = "http://127.0.0.1:9200/articles/_analyze"

    for raw_datum in raw_data:
        # escape some characters or tokenization wont work
        raw_datum[0] = raw_datum[0].replace('\n', '').replace('\r', '').replace("\\", '').replace('"', "") \
            .replace("\b", '').replace("\t", '').replace("\f", '')

        payload = "{\r\n  \"analyzer\" : \"greek_analyzer\",\r\n  \"text\" : \"" + raw_datum[0] + "\"\r\n}"
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload.encode("utf8"))
        response = response.json()

        tokenized = response["tokens"]
        for token in tokenized:
            tokenized_data.append(token["token"])

        tokenized_total.append(tokenized_data)
        tokenized_data = []

    return tokenized_total, raw_type


def get_specific_analyzed(specific_text):
    tokenized_data = []

    url = "http://127.0.0.1:9200/articles/_analyze"

    # escape some characters or tokenization wont work
    specific_text = specific_text.replace('\n', '').replace('\r', '').replace("\\", '').replace('"', "") \
        .replace("\b", '').replace("\t", '').replace("\f", '')

    payload = "{\r\n  \"analyzer\" : \"greek_analyzer\",\r\n  \"text\" : \"" + specific_text + "\"\r\n}"
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload.encode("utf8"))
    response = response.json()

    for token in response["tokens"]:
        tokenized_data.append([token["token"]])

    return tokenized_data


def get_records_per_category():
    records = []
    url = "http://127.0.0.1:9200/articles/_search"
    headers = {
        'Content-Type': 'application/json'
    }

    payload = json.dumps({
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "scope": "ΚΟΣΜΟΣ"
                        }
                    }
                ]
            }
        }
    })
    response = requests.request("GET", url, headers=headers, data=payload.encode("utf8"))
    total_crime_articles_global = response.json()['hits']['total']['value']
    records.append(total_crime_articles_global)

    payload = json.dumps({
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "scope": "ΕΛΛΑΔΑ"
                        }
                    }
                ]
            }
        }
    })
    response = requests.request("GET", url, headers=headers, data=payload.encode("utf8"))
    total_crime_articles = response.json()['hits']['total']['value']
    records.append(total_crime_articles)

    payload = json.dumps({
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "type": "ΔΟΛΟΦΟΝΙΑ"
                        }
                    },
                    {
                        "match": {
                            "scope": "ΕΛΛΑΔΑ"
                        }
                    }
                ]
            }
        }
    })
    response = requests.request("GET", url, headers=headers, data=payload.encode("utf8"))
    murder_crime_number = response.json()['hits']['total']['value']
    records.append(murder_crime_number)

    payload = json.dumps({
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "type": "ΝΑΡΚΩΤΙΚΑ"
                        }
                    },
                    {
                        "match": {
                            "scope": "ΕΛΛΑΔΑ"
                        }
                    }
                ]
            }
        }
    })
    response = requests.request("GET", url, headers=headers, data=payload.encode("utf8"))
    drugs_crime_number = response.json()['hits']['total']['value']
    records.append(drugs_crime_number)

    payload = json.dumps({
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "type": "ΛΗΣΤΕΙΑ/ΚΛΟΠΗ"
                        }
                    },
                    {
                        "match": {
                            "scope": "ΕΛΛΑΔΑ"
                        }
                    }
                ]
            }
        }
    })
    response = requests.request("GET", url, headers=headers, data=payload.encode("utf8"))
    theft_crime_number = response.json()['hits']['total']['value']
    records.append(theft_crime_number)

    payload = json.dumps({
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "type": "ΤΡΟΜΟΚΡΑΤΙΚΗ ΕΠΙΘΕΣΗ"
                        }
                    },
                    {
                        "match": {
                            "scope": "ΕΛΛΑΔΑ"
                        }
                    }
                ]
            }
        }
    })
    response = requests.request("GET", url, headers=headers, data=payload.encode("utf8"))
    terrorism_crime_number = response.json()['hits']['total']['value']
    records.append(terrorism_crime_number)

    payload = json.dumps({
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "type": "ΣΕΞΟΥΑΛΙΚΟ ΕΓΚΛΗΜΑ"
                        }
                    },
                    {
                        "match": {
                            "scope": "ΕΛΛΑΔΑ"
                        }
                    }
                ]
            }
        }
    })
    response = requests.request("GET", url, headers=headers, data=payload.encode("utf8"))
    sex_crime_number = response.json()['hits']['total']['value']
    records.append(sex_crime_number)

    return records


def elastic_greek_stemmer(content):
    url = "http://127.0.0.1:9200/articles/_analyze"

    stemmed_tokens = []

    payload = json.dumps({
        "analyzer": "greek_analyzer",
        "text": content
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload.encode("utf8")).json()
    for token in response['tokens']:
        if len(token['token']) > 2:
            stemmed_tokens.append(token['token'])

    return stemmed_tokens
