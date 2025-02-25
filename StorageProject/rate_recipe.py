from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql.functions import now
from base import Base
import datetime

class RateRecipe(Base):
    """ Rate Recipe """

    __tablename__ = "rate_recipe"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # trace_id = Column(String(250), nullable=False)
    user_id = Column(String(250), nullable=False)
    recipe_id = Column(String(250), nullable=False)
    rating = Column(Float, nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, default=datetime.datetime.now(), nullable=False)

    def __init__(self, user_id, recipe_id, rating, timestamp):
        """ Initializes a recipe rating """
        self.user_id = user_id
        # self.trace_id = trace_id
        self.recipe_id = recipe_id
        self.rating = rating
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now()

    def to_dict(self):
        """ Dictionary Representation of a recipe rating """
        dict = {}
        dict['id'] = self.id
        # dict['trace_id'] = self.trace_id
        dict['user_id'] = self.user_id
        dict['recipe_id'] = self.recipe_id
        dict['rating'] = self.rating
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created

        return dict
