import requests
import re


# for dependency analyze
def gather_raw_verbs(type, threshold):
    url = "http://127.0.0.1:9200/articles/_search"
    keyword = []

    payload = "{\r\n  \"size\":0, \r\n  \"query\": {\r\n    \"match\": {\r\n      \"type\": \""+ type +"\"\r\n   " \
                                                                                                       " }\r\n " \
              " },\r\n  \"aggregations\":{\r\n    \"NAME\":{\r\n      \"significant_text\": {\r\n       " \
              " \"field\": \"body.simple_analyzer\",\r\n        \"size\": " +str(threshold) + "\r\n      }\r\n   " \
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
def get_n_raw_data(crime_type, n):

    url = "http://127.0.0.1:9200/articles/_search"
    total_n_data = []

    payload = "{\r\n  \"size\":" + str(
        n) + ", \r\n  \"query\": {\r\n    \"match\": {\r\n      \"type\": \"" + crime_type + "\"\r\n    }\r\n  }\r\n}"
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload.encode("utf8"))
    response = response.json()

    for datum in response['hits']['hits']:
        data = {
            "Title": datum['_source']['title'],
            "Date": datum['_source']['date'],
            "Body": datum['_source']['body'],
            "Type": datum['_source']['type'],
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


# test
specific_text = "Εμπόριο βρεφών στη Θεσσαλονίκη: Ποιους φακέλους ξεσκονίζει η ΕΛ.ΑΣ. Έρευνα για υποθέσεις που " \
                "σχετίζονται με εμπόριο βρεφών ξεκίνησε η Ασφάλεια Θεσσαλονίκης, ύστερα από την παραγγελία " \
                "προκαταρκτικής εξέτασης από την Εισαγγελία Πρωτοδικών Θεσσαλονίκης, με φόντο τις σοβαρές καταγγελίες " \
                "γυναικών από την Αλβανία για κυκλώματα με έδρα την Ελλάδα. Όλα ξεκίνησαν από μία διπλή δολοφονία στα " \
                "Τίρανα. Εκεί την παραμονή της Πρωτοχρονιάς ένας 59χρονος εκτέλεσε δύο αδερφές, με τις οποίες είχε " \
                "στο παρελθόν ερωτική σχέση. Οι συγγενείς των θυμάτων κατήγγειλαν μετά το έγκλημα στις αλβανικές " \
                "Αρχές ότι ο δράστης εξέδιδε τα δύο θύματα στη Θεσσαλονίκη, τα ανάγκαζε σε κυοφορία και ακολούθως " \
                "πουλούσε τα βρέφη σε άτεκνα ζευγάρια, με τη βοήθεια Έλληνα δικηγόρου από τη βόρεια Ελλάδα.Η Ασφάλεια " \
                "Θεσσαλονίκης έχει ζητήσει μέσω Ιντερπόλ από τις αλβανικές Αρχές το φάκελο με τις σοβαρές καταγγελίες " \
                "για αγοραπωλησίες βρεφών. Από τη μέχρι στιγμής έρευνα προκύπτει ότι τα δύο θύματα είχαν συλληφθεί το " \
                "1992 και το 2003 σε Θεσσαλονίκη και Αθήνα για το νόμο περί αλλοδαπών και εκδιδόμενων προσώπων. Οι " \
                "δύο γυναίκες που δολοφονήθηκαν προσπαθούσαν να ξεφύγουν από τον 59χρονο, ο οποίος τις απειλούσε και " \
                "τις ζήλευε. Η Ελληνική Αστυνομία θα προχωρήσει από εδώ και πέρα στις παρακάτω ενέργειες: Αρχικά θα " \
                "διασταυρώσει εάν με τα ονόματα των δύο αδελφών που δολοφονήθηκαν είχαν γίνει νομιμοφανείς υιοθεσίες " \
                "στη χώρα μας. Αστυνομικές πηγές εξηγούν ότι σε πολλές περιπτώσεις οι διαδικασίες υιοθεσιών φαίνονται " \
                "απολύτως νόμιμες, χωρίς κανείς να γνωρίζει ότι πίσω από αυτές κρύβονται βιασμοί, αναγκαστικές " \
                "κυοφορίες και θύματα μαστροπείας. Τα κυκλώματα εκμεταλλεύονται ευάλωτες γυναίκες, οι οποίες δεν " \
                "προσφεύγουν στις Αρχές. Όπως δηλαδή ακριβώς έγινε και με την περίπτωση των δύο αδελφών από τα " \
                "Τίρανα. Η αλβανική Αστυνομία ενημερώθηκε για τη δράση του 59χρονου αφού είχε γίνει πρώτα το κακό. Οι " \
                "αστυνομικοί θα διασταυρώσουν λοιπόν εάν έγιναν υιοθεσίες, στις οποίες να εμφανίζονται ως μητέρες τα " \
                "δύο θύματα, ενώ ιδιαίτερη προσοχή θα δοθεί σε περιπτώσεις στις οποίες μπορεί να χρησιμοποιήθηκαν " \
                "πλαστά έγγραφα. Το δεύτερο αντικείμενο της έρευνας της ΕΛ.ΑΣ. είναι η έρευνα για τη δράση του " \
                "δικηγόρου. Οι αστυνομικοί θα πάρουν στα χέρια τους το όνομα του Έλληνα δικηγόρου που φέρεται (όπως " \
                "προκύπτει από τις καταγγελίες των συγγενών των θυμάτων) να μεσολαβούσε για τον εντοπισμό αγοραστών " \
                "για τα βρέφη. Το όνομα του δικηγόρου (είτε αυτός βρίσκεται εν ζωή είτε όχι) θα ξεκλειδώσει τις " \
                "έρευνες. Στο παρελθόν η Ασφάλεια Θεσσαλονίκης έχει χειριστεί ξανά υποθέσεις με αγοραπωλησίες βρεφών. " \
                "Στις υποθέσεις αυτές είχαν εμπλοκή δικηγόροι, ενώ τα κυκλώματα είχαν «πλοκάμια» στη γειτονική " \
                "Βουλγαρία. Οι γέννες γίνονταν σε μαιευτήρια στη χώρα μας, οι μητέρες κρατούσαν για λίγες ημέρες τα " \
                "νεογνά και κατόπιν τα παρέδιδαν στους αγοραστές που πλήρωναν αδρά.Οι εγκληματικές οργανώσεις " \
                "εκμεταλλεύονταν την ανάγκη άτεκνων ζευγαριών να υιοθετήσουν ένα παιδί αλλά και τις αυστηρές " \
                "προϋποθέσεις που έθετε ο νόμος για τη διαδικασία. Σημειώνεται ότι η παρέμβαση της Εισαγγελίας " \
                "Πρωτοδικών Θεσσαλονίκης έγινε κατόπιν δημοσιευμάτων με καταγγελίες συγγενών των θυμάτων σε αλβανικά " \
                "μέσα ενημέρωσης, σύμφωνα με τις οποίες ο δράστης, που συνελήφθη και κρατείται, εξέδιδε τις δύο " \
                "αδελφές, τις υποχρέωνε να τεκνοποιούν και στη συνέχεια να πουλούν τα βρέφη τους στην χώρα μας. Όπως " \
                "έγινε γνωστό, ο προϊστάμενος της Εισαγγελίας Πρωτοδικών Θεσσαλονίκης, Παναγιώτης Παναγιωτόπουλος, " \
                "παρήγγειλε την έρευνα στην Ασφάλεια Θεσσαλονίκης, ώστε να διαλευκανθούν οι καταγγελίες περί " \
                "παράνομων υιοθεσιών κι αν υπάρχει εμπλοκή οργανωμένου κυκλώματος. Κατά τις ίδιες καταγγελίες, " \
                "πάνω από δέκα παιδιά γεννήθηκαν σε ελληνικά μαιευτήρια και πωλήθηκαν έναντι αμοιβής με τη βοήθεια " \
                "δικηγόρου που δεν βρίσκεται εν ζωή.Το διπλό φονικό αποκαλύφθηκε την παραμονή της Πρωτοχρονιάς στα " \
                "Τίρανα, όπου οι άτυχες γυναίκες έπεσαν νεκρές από πυρά του 59χρονου, ο οποίος συνελήφθη και " \
                "απολογούμενος προανακριτικά ισχυρίστηκε ότι το κίνητρο της αποτρόπαιης πράξης ήταν η τυφλή ζήλια. "
specific_text.replace('\n', '').replace('\r', '').replace("\\", '').replace('"', "") \
    .replace("\b", '').replace("\t", '').replace("\f", '')

# print(get_specific_analyzed(specific_text))
