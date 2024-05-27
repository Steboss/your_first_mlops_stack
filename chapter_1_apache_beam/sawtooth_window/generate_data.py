import random
from datetime import datetime
import ipaddress
from google.cloud import pubsub_v1
import time
import json
from structlog import get_logger


logger = get_logger()
project_id = "data-gearbox-421420"
topic_id = "input-sawtooth-window"
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)


ipaddresses = [str(ip) for ip in ipaddress.IPv4Network('192.0.2.0/28')]
ipaddresses.extend([str(ip) for ip in ipaddress.IPv4Network('192.1.1.0/28')])
ipaddresses.extend([str(ip) for ip in ipaddress.IPv4Network('192.1.2.0/28')])
ipaddresses.extend([str(ip) for ip in ipaddress.IPv4Network('192.1.4.0/28')])
ipaddresses.extend([str(ip) for ip in ipaddress.IPv4Network('192.0.1.0/28')])
user_addresses = [str(ip) for ip in ipaddress.IPv4Network('192.1.8.0/28')]


def publish_events():
    """ Function to generate events for users and spammers """
    users = [f'user_{i}' for i in range(1000)] # 1000 users
    spammers = [f'user_{i}' for i in range(1,100)]
    # users number 1,-100 are spammers
    while True:
        delay = random.uniform(0.1, 0.9)
        start_time = datetime.now()
        # pick a random user
        random_user = random.choice(users)
        if random_user in spammers:
            # if the random user is a spammer, generate a fail event
            event = {
                'timestamp': start_time.strftime("%Y%m%d%H%M%S"),
                'user_id': random_user,
                'event_type': random.choice(['fail', 'success']), # 50% fail rate
                'source_ip': random.choice(ipaddresses) # change ip address frequently
            }
        else:
            # if the random user is not a spammer, generate a success event
            event = {
                'timestamp': start_time.strftime("%Y%m%d%H%M%S"),
                'user_id': random_user,
                'event_type': 'success',
                'source_ip': random.choice(user_addresses) # change ip address frequently
            }
        message = json.dumps(event)
        publisher.publish(topic_path, message.encode("utf-8"))
        time.sleep(delay)


publish_events()