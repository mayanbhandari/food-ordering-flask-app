from models import db, User, Restaurant
from seed_data import create_seed_data

def seed_if_empty():
    if Restaurant.query.count() == 0:
        create_seed_data()
