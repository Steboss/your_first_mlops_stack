from google.cloud import pubsub_v1
import time
import random
import json
from structlog import get_logger


logger = get_logger()
project_id = "data-gearbox-421420"
topic_id = "example-window-pipeline"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)


def generate_data():
    while True:
        data = {
            "timestamp": int(time.time()),
            "event_type": random.choice(["click", "impression"]),
            "value": random.randint(1, 100)
        }
        logger.info(f"Publishing {data} to {topic_path}")
        message = json.dumps(data)
        publisher.publish(topic_path, message.encode("utf-8"))
        time.sleep(0.2)


if __name__ == "__main__":
    generate_data()