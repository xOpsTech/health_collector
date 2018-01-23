import logging
import constatnts
from elasticsearch import Elasticsearch

es = Elasticsearch(constatnts.ES_IP)
logger = logging.getLogger(__name__)


def search_index_data(index, type, query, is_aggregated_query=False):
    try:
        res = es.search(index=index, doc_type=type, body=query, ignore_unavailable=True)
        if is_aggregated_query:
            return res['aggregations']['products']['buckets']
        else:
            return res['hits']['hits']
    except Exception as e:
        print(e)
