import argparse
import asyncio
import json
import signal
import sys

from kafka import KafkaConsumer

from common.settings import UATConfig
from common.logger import get_logger
from kafka import TopicPartition

_log = get_logger('client')

def _quit_signal_handler(signal_received, frame):
    sig_str = 'SIGINT'
    if signal_received == 15:
        sig_str = 'SIGTERM'
    _log.warning(f'received signal: {sig_str}, exiting...')

    Client.client.commit()
    Client.client.close()

    sys.exit()

signal.signal(signal.SIGTERM, _quit_signal_handler)
signal.signal(signal.SIGINT, _quit_signal_handler)

class Client:
    client = None
    tp = None
    partition = 0

    def __init__(self, partition):
        Client.client = KafkaConsumer(
            group_id=UATConfig.KAFKA_TASK_GROUP_ID,
            bootstrap_servers=UATConfig.KAFKA_RESULT_HOST,
            #auto_offset_reset='earliest',
            enable_auto_commit=False,
            value_deserializer = lambda m: json.loads(m.decode('ascii')),
        )

        Client.partition = partition
        Client.tp = TopicPartition(UATConfig.KAFAK_TASK_TOPIC, Client.partition)

        Client.client.assign([Client.tp])


    async def run(self):
        while True:
            try:
                for task in Client.client:
                    topic_info = f"topic: {task.partition}|{task.offset})"
                    message_info = f"key: {task.key}, {task.value}"
                    _log.info(f"{topic_info}, {message_info}")

                    Client.client.commit()
            except Exception as e:
                _log.error(f'an ERROR happenend in kafka consumption: [{e}]. RESTART consumption loop.')
                Client.client.commit()


async def main():
    parser = argparse.ArgumentParser(
        prog='Kafka consumer',
        description='A Kafka task consumer in HangYun console.')
    parser.add_argument('-p', '--partition', type=int, required=True)
    args = parser.parse_args()

    await Client(args.partition).run()

if __name__ == '__main__':
    asyncio.run(main())
