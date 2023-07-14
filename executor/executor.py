import json
import signal
import subprocess
import sys

from kafka import KafkaConsumer
from kafka import KafkaClient
from kafka import TopicPartition

from common.settings import UATConfig

from common.logger import get_logger

_log = get_logger('executor')

def _quit_signal_handler(signal_received, frame):
    sig_str = 'SIGINT'
    if signal_received == 15:
        sig_str = 'SIGTERM'
    _log.warning(f'received signal: {sig_str}, exiting...')

    for c in Executor.clients:
        c.terminate()

    sys.exit()


signal.signal(signal.SIGTERM, _quit_signal_handler)
signal.signal(signal.SIGINT, _quit_signal_handler)

class Executor:
    clients = []

    def __init__(self):
        self._client = KafkaConsumer(
            UATConfig.KAFAK_TASK_TOPIC,
            group_id=UATConfig.KAFKA_TASK_GROUP_ID,
            bootstrap_servers=UATConfig.KAFKA_RESULT_HOST,
            #auto_offset_reset='earliest',
            enable_auto_commit=False,
            #value_deserializer = lambda m: json.loads(m.decode('ascii')),
        )

        self._topic_partitions = self._client.partitions_for_topic(UATConfig.KAFAK_TASK_TOPIC)

        self._client.close()


    def run(self):
        for p in self._topic_partitions:
            cmd = ['python3', 'client.py','-p', str(p)]
            c = subprocess.Popen(cmd)
            Executor.clients.append(c)

        for c in Executor.clients:
            c.wait()


def main():
    Executor().run()

if __name__ == '__main__':
    main()
