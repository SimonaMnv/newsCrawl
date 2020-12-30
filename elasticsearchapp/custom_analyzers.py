from elasticsearch_dsl import analysis
from elasticsearch_dsl.connections import connections
connections.create_connection()

# TODO: change stopwords, lucene has limited -> import spacy?
array_of_keywords = ["(pics)"]
greek_keywords = analysis.token_filter('greek_keywords', type="keyword_marker", keywords=array_of_keywords)
greek_stemmer = analysis.token_filter('greek_stemmer', type="stemmer", language="greek")

greek_analyzer = analysis.analyzer("greek_analyzer",
                                   type="custom",
                                   tokenizer="standard",
                                   filter=[
                                       analysis.token_filter("greek_lowercase", type="lowercase", language="greek"),
                                       analysis.token_filter('greek_stop', type="stop", stopwords="_greek_"),
                                   ],
                                   )

