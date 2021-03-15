from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from elasticsearchapp.documents import ArticleDocument


class ArticleDocumentSerializer(DocumentSerializer):
    class Meta:
        document = ArticleDocument

        fields = (
            'title',
            'date',
            'body',
            'tags',
            'author',
            'link',
            'type',
            'scope',
            'location_of_crime',
            'ages_of_involved',
            'time_of_crime',
            'victim_gender',
            'acts_committed',
        )
