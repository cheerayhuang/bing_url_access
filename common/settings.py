class UATConfig:
    KAFAK_TASK_TOPIC = r'test-topic-1'
    KAFKA_TASK_RESP_TOPIC = r'test-topic-resp-1'

    KAFKA_RESULT_HOST='127.0.0.1:9092'

    KAFKA_TASK_GROUP_ID = 'executor'
    KAFKA_RESP_GROUP_ID = 'resp-reader'


class LogConfig:
    FORMAT = r'%(asctime)s %(name)s %(filename)s:%(lineno)d:%(funcName)s %(levelname)s %(message)s'
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    LEVEL = "info"


