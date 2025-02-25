import connexion
import json
import os
from datetime import datetime, timezone
import yaml
from connexion import NoContent
from pykafka import KafkaClient
import logging.config
import constant
import uuid

# Determine the environment
if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

# Load application configuration
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

# Load logging configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')
logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

app_conf = app_config['events']
print(f"{app_conf['hostname']}:{app_conf['port']}")
print(f"{app_conf['topic']}")
# Kafka setup 
hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
client = KafkaClient(hosts=hostname)
topic = client.topics[str.encode(app_config["events"]["topic"])]
producer = topic.get_sync_producer(min_queued_messages=100, linger_ms=10)

timestamp = datetime.now(timezone.utc).isoformat()


def write_json(data):
    with open(constant.EVENT_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def time_stamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

def create_recipe(body):
    # Produce message to Kafka
    trace_id = str(uuid.uuid4())
    logger.info(f"Received event create_recipe request with a trace id of {trace_id}")
    body['trace_id'] = trace_id
    msg = {
        "type": "create_recipe",
        "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
    }
    print(f"msg: {msg}")
    producer.produce(json.dumps(msg).encode('utf-8'))
    return NoContent, 201

def rate_recipe(body):
    trace_id = str(uuid.uuid4())
    logger.info(f"Received event rate_recipe request with a trace id of {trace_id}")
    body['trace_id'] = trace_id
    # Produce message to Kafka
    msg = {
        "type": "rate_recipe",
        "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
    }
    producer.produce(json.dumps(msg).encode('utf-8'))
    return NoContent, 201


if __name__ == "__main__":
    app = connexion.FlaskApp(__name__, specification_dir="./")
    app.add_api('IngyuKim_recipes_swagger.yaml', strict_validation=True, validate_responses=True)
    app.run(port=8080, host="0.0.0.0")
