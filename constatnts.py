ES_IP = "elastic.xops.it"
ES_HEALTH_INDEX = "health"
ES_DOC_TYPE = "health"
DATE_FORMAT = "%Y-%m-%d"
SCHEDULER_INTERVAL = 120  # in seconds
TYPE_ITEM = "item"
TYPE_PERFORMANCE = "performance_indicator"

RED_VALUE = 5
ORANGE_VALUE = 4
YELLOW_VALUE = 3
BLUE_VALUE = 2
GREEN_VALUE = 1
OK_VALUE = 0

HEALTH_COLOUR_MAPPING = {
    5.0: 'red',
    4.0: 'orange',
    3.0: 'yellow',
    2.0: 'blue',
    1.0: 'green'
}

QUERY_ITEMS = {
    "query": {
        "match_all": {}
    }
}
QUERY_ITEMS_BY_ID = {
    "query": {
        "term": {
            "_id": "xNews"
        }
    }
}

QUERY_METRIC_VALUE = {
    "query": {
        "bool": {
            "must": [
                {
                    "term": {
                        "id.keyword": {
                            "value": "${metricId}"
                        }
                    }
                },
                {
                    "range": {
                        "timestamp": {
                            "gte": "now-94d"
                        }
                    }
                }
            ]
        }
    },
    "sort": [
        {
            "timestamp": {
                "order": "desc"
            }
        }
    ],
    "_source": [
        "value"
    ],
    "size": 1
}

