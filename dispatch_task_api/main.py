import asyncio
#import random
import json
import time
import uvicorn

from fastapi import FastAPI
from kafka import KafkaProducer, KafkaConsumer
from pydantic import BaseModel, Field, HttpUrl, validator
from typing import List, Union

from common.settings import UATConfig
from common.logger import get_logger

_log = get_logger('dispatcher')

_kafka_prod = KafkaProducer(
    bootstrap_servers=UATConfig.KAFKA_TASK_HOST,
    value_serializer=lambda m: json.dumps(m).encode('ascii'),
)

_kafka_res_consumer = KafkaConsumer(
    UATConfig.KAFKA_TASK_RESP_TOPIC,
    group_id=UATConfig.KAFKA_RESP_GROUP_ID,
    bootstrap_servers=UATConfig.KAFKA_RESULT_HOST,
    #enable_auto_commit=False,
    value_deserializer = lambda m: json.loads(m.decode('ascii')),
)

_kafka_res_reprod = KafkaProducer(
    bootstrap_servers=UATConfig.KAFKA_RESULT_HOST,
    value_serializer=lambda m: json.dumps(m).encode('ascii'),
)

app = FastAPI()

def gen_rand_sid():
    return str(time.time_ns())


def on_send_success(record_meta):
    _log.info(f'send kafka success: topic={record_meta.topic}, partition={record_meta.partition}, offset={record_meta.offset}.')


def on_send_error(ex):
    _log.error('send task faild.', exc_info=ex)


class ReqDataBody(BaseModel):
    urls: List[HttpUrl]
    sid: str = Field(default=gen_rand_sid(), min_length=4, max_length=32)
    max_words: int = Field(default=512, gt = 0, le=2048)

    @validator('urls')
    def validate_urls(urls):
        if len(urls) == 0:
            raise ValueError('urls should NOT be an empty array.')

        return urls


@app.get('/urls/contents')
async def get_urls_contents(data: ReqDataBody):
    t = {}
    t['job_id'] = 'test-topic-1'
    t['data'] = data.dict()

    _log.info(f'data: {t}')

    _kafka_prod.send(t['job_id'], t).add_callback(on_send_success).add_errback(on_send_error)

    res = {}
    for res in _kafka_res_consumer:
        if res.value['sid'] != data.sid:
            _kafka_res_reprod.send(UATConfig.KAFKA_TASK_RESP_TOPIC, res.value).add_callback(on_send_success).add_errback(on_send_error)
            continue
        return  res.value

    return res


if __name__ == '__main__':
    uvicorn.run(app)
