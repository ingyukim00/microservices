from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql.functions import now
from base import Base
import datetime

class CreateRecipe(Base):
    """ Create Recipe """

    __tablename__ = "create_recipe"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # trace_id = Column(String(250), nullable=False)
    user_id = Column(String(250), nullable=False)
    recipe_id = Column(String(250), nullable=False)
    title = Column(String(250), nullable=False)
    ingredients = Column(String(1000), nullable=False)
    instructions = Column(String(1000), nullable=False)
    views = Column(Integer, nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, default=datetime.datetime.now(), nullable=False)

    def __init__(self, user_id, recipe_id, title, ingredients, instructions, views, timestamp):
        """ Initializes a recipe creation event """
        self.user_id = user_id
        # self.trace_id = trace_id
        self.recipe_id = recipe_id
        self.title = title
        self.ingredients = ingredients
        self.instructions = instructions
        self.views = views
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now()

    def to_dict(self):
        """ Dictionary Representation of a recipe creation event """
        dict = {}
        dict['id'] = self.id
        # dict['trace_id'] = self.trace_id
        dict['user_id'] = self.user_id
        dict['recipe_id'] = self.recipe_id
        dict['title'] = self.title
        dict['ingredients'] = self.ingredients
        dict['instructions'] = self.instructions
        dict['views'] = self.views
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created

        return dict
