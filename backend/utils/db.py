from flask import g, current_app
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

def get_db():
    """
    Returns a database session.
    
    Creates a new session if one doesn't exist for the current request.
    """
    if 'db' not in g:
        engine = create_engine(current_app.config['DATABASE_URI'])
        g.db = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    
    return g.db

def close_db(e=None):
    """
    Close the database session at the end of the request.
    """
    db = g.pop('db', None)
    
    if db is not None:
        db.close()

def init_app(app):
    """
    Initialize the database with the Flask app.
    
    Registers the close_db function to be called when the request ends.
    """
    app.teardown_appcontext(close_db) 