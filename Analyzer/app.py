import connexion
import json
from pykafka import KafkaClient
import yaml
import logging.config
from datetime import datetime
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
import os

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
hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"

# Kafka client setup (don't create consumer here)
client = KafkaClient(hosts=hostname)
topic = client.topics[str.encode(app_config["events"]["topic"])]

def get_created_recipes(index):
    """ Get a specific created_recipe by index """
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    count = 0  # Count only "create_recipe" messages
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            event = json.loads(msg_str)
            if event["type"] == "create_recipe":
                if count == index:
                    logger.info(f"Returning created_recipe at index {index}")
                    consumer.stop()  # Close the consumer connection after use
                    return event["payload"], 200
                count += 1
    except Exception as e:
        logger.error(f"Error retrieving created_recipe: {str(e)}")
    finally:
        consumer.stop()  # Ensure the consumer is closed on any error
    logger.warning(f"Could not find created_recipe at index {index}")
    return {"message": "Not Found"}, 404

def get_rated_recipes(index):
    """ Get a specific rated_recipe by index """
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    count = 0
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            event = json.loads(msg_str)
            if event["type"] == "rate_recipe":
                if count == index:
                    logger.info(f"Returning rated_recipe at index {index}")
                    consumer.stop()
                    return event["payload"], 200
                count += 1
    except Exception as e:
        logger.error(f"Error retrieving rated_recipe: {str(e)}")
    finally:
        consumer.stop()
    logger.warning(f"Could not find rated_recipe at index {index}")
    return {"message": "Not Found"}, 404

def get_event_stats():
    """ Get statistics for events in the message queue """
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    num_cr, num_rr = 0, 0
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            event = json.loads(msg_str)
            if event["type"] == "create_recipe":
                num_cr += 1
            elif event["type"] == "rate_recipe":
                num_rr += 1
        logger.info("Returning event stats")
    except Exception as e:
        logger.error(f"Error calculating stats: {str(e)}")
        return {"message": "Error calculating stats"}, 500
    finally:
        consumer.stop()  # Always stop the consumer
    return {
        "num_cr": num_cr,
        "num_rr": num_rr,
        "last_updated": datetime.now().isoformat()
    }, 200

app = connexion.FlaskApp(__name__, specification_dir='./')
app.add_middleware(
    CORSMiddleware,
    position=MiddlewarePosition.BEFORE_EXCEPTION,
    allow_origins=["*"],          # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],           # Allow all HTTP methods
    allow_headers=["*"]            # Allow all headers
)
app.add_api("IngyuKim_recipes_swagger.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110, host="0.0.0.0")
