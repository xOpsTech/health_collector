import EsReader
import constatnts
from Item import Item
from PerfIndicator import PerfIndicator
from elasticsearch import Elasticsearch
from datetime import datetime
import pytz

utc = pytz.utc

es = Elasticsearch(constatnts.ES_IP)


class HealthCalculator(object):
    def __init__(self, tenant_id):
        self.tenantId = tenant_id
        self.item_index = 'item-indicators-' + tenant_id
        self.index_type = 'configs'
        self.metrics_index = 'metrics-' + tenant_id

    def get_items(self):
        return EsReader.search_index_data(self.item_index, self.index_type, constatnts.QUERY_ITEMS)

    def get_items_by_id(self, item_id):
        query = constatnts.QUERY_ITEMS_BY_ID
        query['query']['term']['_id'] = item_id
        es_result = EsReader.search_index_data(self.item_index, self.index_type, query)
        result = []

        if es_result:
            result = es_result[0]['_source']['perfIndicators']

        return result

    def get_metric_value(self, perf_id):
        query = constatnts.QUERY_METRIC_VALUE
        query['query']['bool']['must'][0]['term']['id.keyword'] = perf_id
        es_result = EsReader.search_index_data(self.metrics_index, None, query)
        result = 0

        if es_result:
            result = es_result[0]['_source']['value']

        return result

    def start(self):
        items = self.get_items()

        for item in items:
            try:
                item_id = item['_id']
                importance = item['_source']['importance']
                perf_indicators = item['_source']['perfIndicators']

                # item_obj = Item()
                # item.id = item_id
                # item.importance = item['importance']

                if perf_indicators:
                    try:
                        health, health_list, _ = self.gather_health(item, perf_indicators)
                        health_result = self.compose_msg(item_id, health, importance, health_list)
                        print(health_result)
                        self.write_to_es(health_result)
                        # print(item_id, ':', health, health_list)
                    except Exception as ex:
                        print('Error in calculating health | tenant: %s | item: %s | error: %s' % (
                            self.tenantId, item_id, ex))
            except Exception as ex:
                print('Error in reading items | tenant: %s | error: %s' % (self.tenantId, ex))
        else:
            print('No items configured | tenant: %s' % self.tenantId)

    def gather_health(self, current_item, item_list):

        if len(item_list) == 0:
            # we have hit the bottom, it's a perf indicator

            current_item_id = current_item['id']
            metric_value = self.get_metric_value(current_item_id)
            perf_indicator = PerfIndicator()
            perf_indicator.id = current_item_id
            perf_indicator.is_boolean = current_item.get('isBoolean', False)
            perf_indicator.red_threshold = current_item['thresholdRed']
            perf_indicator.orange_threshold = current_item['thresholdOrange']
            perf_indicator.yellow_threshold = current_item['thresholdYellow']
            perf_indicator.blue_threshold = current_item['thresholdBlue']
            perf_indicator.green_threshold = current_item['thresholdGreen']
            perf_indicator.value = metric_value
            perf_indicator.importance = current_item['importance']

            perf_indicator.calculate_health_value()
            return perf_indicator.health_value, None, perf_indicator.is_boolean
        else:

            total_health_value = 0
            total_importance = 0
            health_list = []
            is_bool_list = []
            for item in item_list:
                item_id = item['id']
                importance = item['importance']
                items = self.get_items_by_id(item_id)

                health_value, prev_health_list, is_boolean = self.gather_health(item, items)

                if is_boolean:
                    print('isBoolean true for %s | health_value: %s' % (item_id, health_value))
                    is_bool_list.append(health_value)

                health_list.append(self.compose_msg(item_id, health_value, importance, prev_health_list))

                if len(is_bool_list) > 0:
                    continue

                total_health_value += health_value * importance
                total_importance += importance

            if len(is_bool_list) > 0:
                health = max(is_bool_list)
                print('max health for %s | health_value: %s' % (item_id, health))
            else:
                health = total_health_value / total_importance
            return health, health_list, None

    def compose_msg(self, item_id, health_value, importance, health_list):

        status = get_health_status(health_value)

        if health_list:
            return {'id': item_id, 'health_value': health_value, 'status': status, 'importance': importance,
                    'perf_list': health_list}
        else:
            return {'id': item_id, 'health_value': health_value, 'status': status, 'importance': importance}

    def write_to_es(self, health_result):
        try:
            item_id = health_result['id']
            utc_now = utc.localize(datetime.utcnow())

            timestamp = get_timestamp(utc_now)
            es_index = constatnts.ES_HEALTH_INDEX + "-" + self.tenantId + "-" + get_today(utc_now)

            health_result['timestamp'] = timestamp
            es_result = es.index(index=es_index, doc_type=constatnts.ES_DOC_TYPE, body=health_result)
            print('process: write to es | item: %s | index: %s | id: %s | status: successful' % (
                item_id, es_index, es_result['_id']))
        except Exception as e:
            print(
                'process: write to es | id: %s | index: %s | newrelic_metric: %s | status: unsuccessful | reason: %s' % (
                    item_id, es_index, health_result, e))


def get_timestamp(utc_now):
    return int((utc_now - datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds() * 1000)


def get_today(utc_now):
    return datetime.strftime(utc_now, constatnts.DATE_FORMAT)


def get_health_status(health_value):
    rounded_health_value = round(health_value)
    status = constatnts.HEALTH_COLOUR_MAPPING.get(rounded_health_value, 'green')
    return status


if __name__ == '__main__':
    healthC = HealthCalculator('xtenant_new')
    healthC.start()
