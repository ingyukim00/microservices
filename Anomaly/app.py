import connexion
import json
from pykafka import KafkaClient
import yaml
import logging.config
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
import os
from operator import itemgetter

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
logger.info(hostname)
# Kafka client setup (don't create consumer here)
client = KafkaClient(hosts=hostname)
topic = client.topics[str.encode(app_config["events"]["topic"])]

# JSON file for storing anomalies
anomalies_file = app_config['events']['datastore']['filename']

def write_to_json_file(data):
    """Write data to the JSON file."""
    try:
        with open(anomalies_file, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error writing to JSON file: {e}")

def read_from_json_file():
    """Read data from the JSON file."""
    try:
        if not os.path.exists(anomalies_file):
            return []
        with open(anomalies_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading from JSON file: {e}")
        return []

def populate_anomalies():
    """Consume Kafka events, detect anomalies, and store them in a JSON file."""
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    anomalies = read_from_json_file()
    try:
        for msg in consumer:
            if msg is None:
                continue
            msg_str = msg.value.decode('utf-8')
            event = json.loads(msg_str)
            logger.info(f"Consumed event: {event}")

            anomaly = None  # Initialize anomaly at the start of the loop

            if event['type'] == "create_recipe":
                views = event["payload"]["views"]
                if views > app_config["events"]["thresholds"]["views_high"]:
                    anomaly = {
                        "event_id": event["payload"]["recipe_id"],
                        "trace_id": event["payload"]["trace_id"],
                        "event_type": event['type'],
                        "anomaly_type": "Too High",
                        "description": f"Views of {views} exceed the threshold of {app_config['events']['thresholds']['views_high']}.",
                        "timestamp": datetime.now().isoformat() + 'Z'
                    }
                elif views < app_config["events"]["thresholds"]["views_low"]:
                    anomaly = {
                        "event_id": event["payload"]["recipe_id"],
                        "trace_id": event["payload"]["trace_id"],
                        "event_type": event['type'],
                        "anomaly_type": "Too Low",
                        "description": f"Views of {views} are below the threshold of {app_config['events']['thresholds']['views_low']}.",
                        "timestamp": datetime.now().isoformat() + 'Z'
                    }

            elif event['type'] == "rate_recipe":
                rating = event["payload"]["rating"]
                if rating > app_config["events"]["thresholds"]["rating_high"]:
                    anomaly = {
                        "event_id": event["payload"]["recipe_id"],
                        "trace_id": event["payload"]["trace_id"],
                        "event_type": event["type"],
                        "anomaly_type": "Too High",
                        "description": f"Rating of {rating} exceeds the threshold of {app_config['events']['thresholds']['rating_high']}.",
                        "timestamp": datetime.now().isoformat() + 'Z'
                    }
                elif rating < app_config["events"]["thresholds"]["rating_low"]:
                    anomaly = {
                        "event_id": event["payload"]["recipe_id"],
                        "trace_id": event["payload"]["trace_id"],
                        "event_type": event["type"],
                        "anomaly_type": "Too Low",
                        "description": f"Rating of {rating} is below the threshold of {app_config['events']['thresholds']['rating_low']}.",
                        "timestamp": datetime.now().isoformat() + 'Z'
                    }

            # Check for duplicates before appending
            if anomaly:
                is_duplicate = any(
                    a["event_id"] == anomaly["event_id"] and a["anomaly_type"] == anomaly["anomaly_type"]
                    for a in anomalies
                )
                if not is_duplicate:
                    anomalies.append(anomaly)
                    logger.info(f"Anomaly detected and added: {anomaly}")
                else:
                    logger.info(f"Duplicate anomaly detected, skipping: {anomaly}")

        # Write anomalies to the JSON file
        write_to_json_file(anomalies)

    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
    finally:
        consumer.stop()

def get_anomalies(anomaly_type):
    """Retrieve anomalies by type, sorted from newest to oldest."""
    anomalies = read_from_json_file()
    filtered_anomalies = [a for a in anomalies if a["anomaly_type"] == anomaly_type]
    sorted_anomalies = sorted(filtered_anomalies, key=itemgetter("timestamp"), reverse=True)
    logger.info(f"GET /anomalies?name={anomaly_type} returned {len(sorted_anomalies)} anomalies.")
    return sorted_anomalies, 200

def init_scheduler():
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(func=populate_anomalies, trigger="interval", seconds=app_config['scheduler']['period_sec'])
    scheduler.start()

app = connexion.FlaskApp(__name__, specification_dir='./')
app.add_middleware(
    CORSMiddleware,
    position=MiddlewarePosition.BEFORE_EXCEPTION,
    allow_origins=["*"],          # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],          # Allow all HTTP methods
    allow_headers=["*"]           # Allow all headers
)
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    logger.info(f"Starting Anomaly Detector Service on port 8120 with thresholds: {app_config['events']['thresholds']}")
    init_scheduler()
    app.run(port=8120, host="0.0.0.0")
