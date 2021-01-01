from django_elasticsearch_dsl import Index, fields
from django_elasticsearch_dsl.documents import DocType
from elasticsearch_dsl import analyzer
from api.models.article_model import ArticleOfInterest
from elasticsearch_dsl.connections import connections
from django_elasticsearch_dsl.registries import registry

connections.create_connection()

article_index = Index('articles')

article_index.settings(
    number_of_shards=1,
    number_of_replicas=0
)


@registry.register_document
@article_index.document
class ArticleDocument(DocType):
    id = fields.TextField(attr='_id')

    title = fields.TextField(
        attr='title',
        fields={
            'suggest': fields.Completion(),
        }
    )
    date = fields.DateField()

    body = fields.TextField(
        attr='body',
        fields={
            'suggest': fields.Completion(),
        }
    )

    tags = fields.TextField(
        attr='tags',
        fields={
            'suggest': fields.Completion(),
        }
    )

    author = fields.TextField(
        attr='author',
        fields={
            'suggest': fields.Completion(),
        }
    )

    link = fields.TextField(
        attr='link',
        fields={
            'suggest': fields.Completion(),
        }
    )

    class Django:
        model = ArticleOfInterest


# sync django / elastic:
# 1. create elasticsearchapp indexes: python manage.py elasticsearchapp --create -f
# 2. sync data: python manage.py elasticsearchapp --populate -f

# TODO: python manage.py search_index --rebuild
