from bson.objectid import ObjectId
from api.models.article_model import ArticleOfInterest
import re
from twisted.internet.threads import deferToThread
import hashlib
from ML.POS.pos import analyse_victim
from ML.classification.ML_classification import classify_crime_type

drugs_list = ['Μαριχουάνα', 'Χασίς', 'Κοκαΐνη', 'Ηρωίνη', 'Μορφίνη', 'LSD', 'STP', 'Βαρβιτουρικά',
              'κάνναβη', 'Αμφεταμίνες', 'Αμφεταμίνη', 'Κεταμίνη', 'Μεθαμφεταμίνη', 'Rohypnol', 'Κρακ',
              'Παραισθησιογόνα']


class DjangoPipeline(object):
    collection_name = 'scrapy_articles'

    def process_item(self, item, spider):
        return deferToThread(self._process_item, item, spider)

    def _process_item(self, item, spider):
        body = item["body"]

        # 1. remove junk sentences from body
        body_junkyard = ["Ειδήσεις από την Ελλάδα", "Διαβάστε ΕΔΩ περισσότερα", "Πηγή",
                         "Διαβάστε επίσης", "Δείτε όλες τις τελευταίες", "Δείτε φωτογραφίες", "Δείτε το βίντεο"]
        recycled_body = [[re.search("(?:(?!" + junk + ").)*", body).group() for junk in body_junkyard]]

        # 2. if there is no space after dot, add one
        add_space_after_dot = r"\.(?=\S)"
        final_body = [re.sub(add_space_after_dot, ". ", body) for body in recycled_body[0]]

        hashed_id = hashlib.md5(item["link"].encode()).hexdigest()

        # run the ML, POS, Elastic analysis on the title+body
        content = item["title"] + min(final_body, key=len)
        article_summary, victim_gender, criminal_status, act, age, date, specific_person, location = analyse_victim(
            content, item["type"])

        # text mine the drug
        specific_drug = ""
        for drug in drugs_list:
            if drug in content or drug.lower() in content:
                specific_drug = drug

        # classify whatever is in "ΑΛΛΟ ΕΓΚΛΗΜΑ" to match a crime category
        if item["type"] == 'ΑΛΛΟ ΕΓΚΛΗΜΑ' and item["scope"] == 'ΕΛΛΑΔΑ':
            ML_crime_type = classify_crime_type(content)

            article = ArticleOfInterest(_id=str(ObjectId(hashed_id[:24])), title=item["title"], date=item["date"],
                                        body=min(final_body, key=len), tags=item["tags"], author=item["author"],
                                        link=item["link"], type=ML_crime_type, scope=item["scope"],
                                        victim_gender=victim_gender, criminal_status=criminal_status, acts_committed=act,
                                        ages_of_involved=age, time_of_crime=date, person_involved=specific_person,
                                        location_of_crime=location, drug_type=specific_drug)
        else:
            article = ArticleOfInterest(_id=str(ObjectId(hashed_id[:24])), title=item["title"], date=item["date"],
                                        body=min(final_body, key=len), tags=item["tags"], author=item["author"],
                                        link=item["link"], type=item["type"], scope=item["scope"],
                                        victim_gender=victim_gender, criminal_status=criminal_status, acts_committed=act,
                                        ages_of_involved=age, time_of_crime=date, person_involved=specific_person,
                                        location_of_crime=location, drug_type=specific_drug)

        article.save()
        return item
