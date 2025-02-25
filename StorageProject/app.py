import connexion
import json
import os
from datetime import datetime
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from create_recipe import CreateRecipe
from rate_recipe import RateRecipe
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
import yaml
import logging.config
from flask import jsonify

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

# Initialize logger
logger = logging.getLogger('basicLogger')
logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

app_conf = app_config["events"]

db_config = app_config["datastore"]
# Log the MySQL hostname and port
logger.info(
    f"Connecting to DB. Hostname: {db_config['hostname']}, Port: {db_config['port']}"
)
DB_ENGINE = create_engine(
    f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['hostname']}:"
    f"{db_config['port']}/{db_config['db']}",
    pool_size=10,            # Increase pool size for higher concurrency
    pool_recycle=60 * 5,       # Recycle connections after 30 minutes (1800 seconds)
    pool_pre_ping=True       # Enable pre-ping to check connection validity
)
Base.metadata.create_all(DB_ENGINE)
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def time_stamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")


def get_all_recipes():
    session = DB_SESSION()
    recipes = session.query(CreateRecipe).all()
    session.close()
    return jsonify([recipe.to_dict() for recipe in recipes]), 200


def get_all_ratings():
    session = DB_SESSION()
    ratings = session.query(RateRecipe).all()
    session.close()
    return jsonify([rating.to_dict() for rating in ratings]), 200


def convert_from_iso_8601_timestamp(iso_8601):
    # logger.info(f"iso_8601 is {iso_8601}")
    try:
        # Parse the ISO 8601 string to a datetime object
        timestamp_obj = datetime.fromisoformat(
            iso_8601.replace("Z", "+00:00")
        )  # Handle UTC 'Z'
        # logger.info(f"this is timestamp_obj: {timestamp_obj}")
        # Return the datetime object or format it to your desired string format
        timestamp_str = timestamp_obj.strftime("%Y-%m-%d %H:%M:%S.%f")
        logger.debug(f"Converted ISO 8601 timestamp {iso_8601} to {timestamp_str}")
        return timestamp_str
    except Exception as e:
        logger.error(f"Error converting timestamp: {e}")
        raise


def process_messages():
    """Process event messages"""
    hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Create a consumer that only reads new messages
    consumer = topic.get_simple_consumer(
        consumer_group=b"event_group",  # byte string or bytes literal rather than a regular text (Unicode) string
        reset_offset_on_start=False,
        auto_offset_reset=OffsetType.LATEST,
    )

    for msg in consumer:
        try:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            logger.info("Message: %s" % msg)

            payload = msg["payload"]
            if msg["type"] == "create_recipe":
                session = DB_SESSION()
                cr = CreateRecipe(
                    user_id=payload['user_id'],
                    recipe_id=payload['recipe_id'],
                    title=payload['title'],
                    ingredients=payload['ingredients'],
                    instructions=payload['instructions'],
                    views=payload['views'],
                    timestamp=convert_from_iso_8601_timestamp(payload['timestamp'])
                )
                session.add(cr)
                session.commit()
                logger.info(f"Stored create_recipe event with recipe_id {payload['recipe_id']}")
            elif msg["type"] == "rate_recipe":
                session = DB_SESSION()
                rr = RateRecipe(
                    user_id=payload['user_id'],
                    recipe_id=payload['recipe_id'],
                    rating=payload['rating'],
                    timestamp=convert_from_iso_8601_timestamp(payload['timestamp'])
                )
                session.add(rr)
                session.commit()
                logger.info(f"Stored rate_recipe event with recipe_id {payload['recipe_id']}")
            consumer.commit_offsets()
        except Exception as e:
            logger.error(f"Error processing message: {e}")
        finally:
            session.close()


app = connexion.FlaskApp(__name__, specification_dir="./")
app.add_api(
    "IngyuKim_recipes_swagger.yaml", strict_validation=True, validate_responses=True
)

if __name__ == "__main__":
    # Start the Kafka consumer in a separate thread
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090, host="0.0.0.0")
