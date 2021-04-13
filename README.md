# Greek Crime Analyzer

## Table of contents

* [General info](#general-info)
* [Technologies](#technologies)
* [Database Model](#database-model)
* [Crawling Layer](#crawling-layer)
* [Classifying Layer](#classifying-layer)
* [Crime Analysis](#crime-analysis)
* [UI](#ui)

## General info

Greek Crime Analyzer is a project that consists of:
1. Crawling and storing greek crime articles in MongoDB
2. Classifying them to a crime type using SVM classifier [custom-trained model, adaptable]
3. Analyzing them using machine learning (NLP) and elastic custom analyzers to create additional json fields to the final analysis.
4. UI with all the articles available and their text analysis, pie charts, a map with crime-coordinate locations

## Technologies

| |Version|
| ------------- |:-------------:|
| Python         |3.8  |
| Elasticsearch | 7.10.1|
| Dash | 1.18.1|
| Scrapy| 2.4.1|
| Spacy |2.3.5 |
| Django| 3.1.4|

### Requirements

install frozen-requirements from the main folder and requirements from the dash subfolder

## Database Model
The database model follows a noSQL schema can be found in ```api/models/article_model``` 
Diagram of the schema:
![mongodb](https://user-images.githubusercontent.com/59322298/114606705-46b88700-9ca4-11eb-9c64-557481f09c4e.PNG)

### Crawling Layer

For the crawling layer, scrapy is deployed. The spider can be found in ```crawling/spiders/newsbomb_spider.py```
The spider's tasks are:
1. Performs text mining from the article's url to find some basic information, e.g. the article's scope (Greece / Global)
2. Uses many start URL's to crawl for many different crime types
3. Extracts information from each URL (title, date, body, tags, author, link, type, scope)
4. The spider uses the pipelines.py in ```crawling/crawling/pipelines.py``` to further customly clear the downloaded data
5. In the pipelines, the spider also performs crime-analysis for each article and creates a new record to the mongoDB

After the crawling is over, we synchronize the mongoDB with the elastic database using ```python manage.py search_index --rebuild```
An example of 1 elastic article record (after the crime-analysis process) can be seen below:
![elastic](https://user-images.githubusercontent.com/59322298/114608742-ac0d7780-9ca6-11eb-83b4-65445da93177.PNG)

### Classifying Layer

This layer is used to classify an article and categorize it in one of the following categories: murder, drugs, theft, sexual crime, terrorism. This layer is enabled, in combination with the analysis layer, when a new article is crawled.
The classifier is custom-trained by using greek crime articles that had available "tags" by the article's author. Tags that implied a crime type were text mined to create a custom annotated dataset. The classifier with a UI can also be found as a standalone project: https://github.com/SimonaMnv/ArachneClassifier

### Crime Analysis

For the analysis of the text two methods were deployed:
1. NLP (Spacy, NLTK e.t.c)
2. Elasticsearch analyzers 

**Elasticseach analyzers**:
in ```elasticsearchapp/documents.py``` the schema of elastic is defined. The same fields as in mongo are applied, but the "title" and "body" fields are enriched with analyzers. More specifically, a custom greek analyzer has been created to lowercase, remove stopwords (extra stopwords from spacy added), apply a stemmer.

We communicate with our elastic using queries. All of the project's elastic queries are located in ```elasticsearchapp/query_results```

**Analyzing process**:
1. For the victims gender a custom strategy has been deployed. Text mining is used for the very basic words that imply a specific gender and a dependency collector (https://explosion.ai/demos/displacy) is used to identify the gender if the text mining fails. The dependecy collector is applied on a "summarized" set of sentences extracted from the title+body. 
Elastic has a built-in TF-IDF (https://sci2lab.github.io/ml_tutorial/tfidf/) which is used to collect all the top (based on a threshold) verbs in each crime category. From all the 4K murder cases (for example) that we have, we find the top 50 verbs that are most frequently repeated throughout the database. After than, we also collect all the local verbs, from the currect article given and extract the sentences where we have matching verbs. In that way, we create a "summary" of the article that includes only important verbs. This helps us keep only the very important information to extract the gender of the victim as it is most likely to be in those sentences due to the fact that verbs imply an act.
2. For the "crime status", simply, text mining is used
3. For the "acts", "age", "date", a custom-trained NER model is used. The model can be located in ```ML/NER/custom_model``` and is trained on ~50 articles by using a NER annotator tool (https://github.com/ManivannanMurugavel/spacy-ner-annotator). Further annotation is required for accuracy improvement
4. For the "location", SpaCy's greek NER is used

### Crime Analysis

For the UI, plotly's dash (runs on flask) is deployed. The crime dash in ```dash/crime_dash.py``` uses elastic's api calls to retrieve the analyzed data. 
click to see a preview: https://user-images.githubusercontent.com/59322298/114617279-9f8e1c80-9cb0-11eb-9edf-71c4829cb41a.mp4

