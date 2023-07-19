import json


from kafka import KafkaConsumer

from common.settings import UATConfig

consumer = KafkaConsumer(
    UATConfig.KAFAK_TASK_TOPIC,
    #bootstrap_servers=["localhost:9092"],
    bootstrap_servers=UATConfig.KAFKA_RESULT_HOST,
    group_id="test",
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    #value_deserializer = lambda m: json.loads(m.decode('ascii')),
    consumer_timeout_ms=1000
)

#consumer.subscribe("test-topic-1")

try:
    for message in consumer:
        topic_info = f"topic: {message.partition}|{message.offset})"
        message_info = f"key: {message.key}, {message.value}"
        print(f"{topic_info}, {message_info}")
except Exception as e:
    print(f"Error occurred while consuming messages: {e}")
finally:
    consumer.close()
