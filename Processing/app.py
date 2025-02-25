import json
import connexion
import requests
from flask import jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
import statistics
import os
import yaml
import logging.config
from datetime import datetime
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware

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

storage_url = app_config['eventstore']['url']

# Dictionary to hold the stats
stats = {
    "num_recipes": 0,
    "num_ratings": 0,
    "avg_recipe_view_value": 0.0,
    "avg_ratings_rating_value": 0.0,
    "median_recipe_view_value": 0.0,
    "median_ratings_rating_value": 0.0,
}


def populate_stats():
    """ Periodically update stats """
    logger.info("Start Periodic Processing")
    logger.info(f"this is app_config file: {app_config['datastore']['filename']}")
    if not os.path.exists(app_config['datastore']['filename']):
        logger.info(f"{app_config['datastore']['filename']} does not exist.")
        with open(app_config['datastore']['filename'], 'w') as file:
            json.dump(stats, file, indent=4)
    
    try:
        response_recipes = requests.get(f"{storage_url}/recipe/all")
        response_ratings = requests.get(f"{storage_url}/rating/all")
        
        if response_recipes.status_code == 200 and response_ratings.status_code == 200:
            recipe_data = response_recipes.json()
            rating_data = response_ratings.json()

            # Log number of events received
            logger.info(f"Received {len(recipe_data)} recipe events and {len(rating_data)} rating events")

            # Update recipe stats
            stats["num_recipes"] = len(recipe_data)
            if recipe_data:
                views = [recipe["views"] for recipe in recipe_data]
                stats["avg_recipe_view_value"] = sum(views) / len(views)
                stats["median_recipe_view_value"] = statistics.median(views)

            # Update rating stats
            stats["num_ratings"] = len(rating_data)
            if rating_data:
                ratings = [rating["rating"] for rating in rating_data]
                stats["avg_ratings_rating_value"] = sum(ratings) / len(ratings)
                stats["median_ratings_rating_value"] = statistics.median(ratings)

            # Update last_updated timestamp
            stats["last_updated"] = datetime.now().isoformat() + 'Z'

            # Log updated stats
            logger.debug(f"Updated stats: {json.dumps(stats, indent=2)}")

        else:
            if response_recipes.status_code != 200:
                logger.error(f"Failed to retrieve recipes: {response_recipes.status_code}")
            if response_ratings.status_code != 200:
                logger.error(f"Failed to retrieve ratings: {response_ratings.status_code}")

    except Exception as e:
        logger.error(f"Error during stats update: {e}")

    # Write updated stats back to JSON file
    with open(app_config['datastore']['filename'], 'w') as file:
        json.dump(stats, file, indent=4)
    logger.info("Periodic Processing Ended")


def get_stats():
    """
    GET /stats endpoint to retrieve the event statistics.
    """
    # Retrieve the start_timestamp and end_timestamp from query parameters
    logger.info("GET /stats request has started")
    try:
        with open(app_config['datastore']['filename'], 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        logger.error("Statistics do not exist.")
        return jsonify({"message": "Statistics do not exist"}), 404
    response = {
        "num_recipes": data["num_recipes"],
        "num_ratings": data["num_ratings"],
        "avg_recipe_view_value": data["avg_recipe_view_value"],
        "avg_ratings_rating_value": data["avg_ratings_rating_value"],
        "median_recipe_view_value": data["median_recipe_view_value"],
        "median_ratings_rating_value": data["median_ratings_rating_value"],
        "last_updated": data["last_updated"]
    }

    logger.debug(f"Returning stats: {json.dumps(response, indent=2)}")

    logger.info("GET /stats request has completed")

    return jsonify(response), 200


# Schedule periodic statistics
# updates get_stats() should run only when a user runs but update_stats() continuously
# runs in the background, so it's up-to-date
def init_scheduler():
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(func=populate_stats, trigger="interval", seconds=app_config['scheduler']['period_sec'])
    scheduler.start()


app = connexion.FlaskApp(__name__, specification_dir="./")
app.add_middleware(
    CORSMiddleware,
    position=MiddlewarePosition.BEFORE_EXCEPTION,
    allow_origins=["*"],          # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],           # Allow all HTTP methods
    allow_headers=["*"]            # Allow all headers
)
app.add_api('IngyuKim_recipes_swagger.yaml', strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, host="0.0.0.0")
