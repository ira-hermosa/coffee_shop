import os
from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy
import json

database_filename = "database.db"
project_dir = os.path.dirname(os.path.abspath(__file__))
database_path = "sqlite:///{}".format(
    os.path.join(project_dir, database_filename))

db = SQLAlchemy()

# Set up db, binding flask application and a SQLAlchemy service
def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

# Drops the db tables and starts fresh upon server refresh
# Can be used to initalise a clean database
    db.drop_all()
    db.create_all()

# Drink model


class Drink(db.Model):

    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    title = Column(String(80), unique=True)
    # the ingredients blob - this stores a lazy json blob
    # the required datatype is [{'color': string, 'name':string,
    # 'parts':number}]
    recipe = Column(String(180), nullable=False)

    # Short form representation of the Drink model
    def short(self):
        print(json.loads(self.recipe))
        short_recipe = [{'color': r['color'], 'parts': r['parts']}
                        for r in json.loads(self.recipe)]
        return {
            'id': self.id,
            'title': self.title,
            'recipe': short_recipe
        }

    # Long form representation of the Drink model
    def long(self):
        return {
            'id': self.id,
            'title': self.title,
            'recipe': json.loads(self.recipe)
        }

    # Inserts a new model into a database
    def insert(self):
        db.session.add(self)
        db.session.commit()

    # Deletes an existing model in a database
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    # Updates an existing model in a database
    def update(self):
        db.session.commit()

    def __repr__(self):
        return json.dumps(self.short())
