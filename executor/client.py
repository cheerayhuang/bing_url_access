import nest_asyncio
#nest_asyncio.apply()

import argparse
import asyncio
import json
import signal
import sys

from kafka import KafkaConsumer
from kafka import TopicPartition

from common.settings import UATConfig
from common.logger import get_logger
from browser import Browser

_log = get_logger('client')

def _quit_signal_handler(signal_received, frame):
    sig_str = 'SIGINT'
    if signal_received == 15:
        sig_str = 'SIGTERM'
    _log.warning(f'received signal: {sig_str}, exiting...')

    Client._client.commit()
    Client._client.close()
    client._browser.close()

    sys.exit()

signal.signal(signal.SIGTERM, _quit_signal_handler)
signal.signal(signal.SIGINT, _quit_signal_handler)

class Client:
    _client = None
    _tp = None
    _partition = 0

    _browser = None

    async def __new__(cls, *args, **kargs):
        obj = super().__new__(cls)
        Client._client = KafkaConsumer(
            group_id=UATConfig.KAFKA_TASK_GROUP_ID,
            bootstrap_servers=UATConfig.KAFKA_RESULT_HOST,
            #auto_offset_reset='earliest',
            enable_auto_commit=False,
            value_deserializer = lambda m: json.loads(m.decode('ascii')),
        )

        Client._partition = kargs['partition']
        Client._tp = TopicPartition(UATConfig.KAFAK_TASK_TOPIC, Client._partition)

        Client._client.assign([Client._tp])

        Client._browser = await Browser()


        return obj


    def __init__(self):
        pass


    async def handle(self, data):
        sid = data['sid']

        for url in data['urls']:
            contents = await Client._browser.get_page_contents(url)
            _log.info(f'contents:\n{contents}')

    async def run(self):
        while True:
            try:
                for task in Client._client:
                    topic_info = f"topic: {task.partition}|{task.offset})"
                    message_info = f"key: {task.key}, {task.value}"
                    _log.info(f"{topic_info}, {message_info} {type(task.value)}")

                    Client._client.commit()

                    await self.handle(task.value['data'])
            except Exception as e:
                _log.warning(f'an ERROR happenend in kafka consumption: [{e}]. RESTART consumption loop.')
                Client._client.commit()


async def main():
    parser = argparse.ArgumentParser(
        prog='Kafka consumer',
        description='A Kafka task consumer in HangYun console.')
    parser.add_argument('-p', '--partition', type=int, required=True)
    args = parser.parse_args()

    c = await Client(partition=args.partition)
    await c.run()

if __name__ == '__main__':
    asyncio.run(main())
