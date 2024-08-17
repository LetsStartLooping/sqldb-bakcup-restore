# Create Sample DB

from sqlalchemy import create_engine, Column, Integer, String, Sequence, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create a local SQLite DB
# If DB doesn't exist then it will create it, 
# else it will just return the `engine` that points to the SQLite DB
engine = create_engine('sqlite:///my_sql_db.db', echo=True)


# Base class for the DB Models
Base = declarative_base()

# Define DB Tables using Python Classes
# These classes should inherit from the `Base`
class User(Base):
    
    # This will be the table name in the SQLite DB
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    
class Task(Base):
    
    # This will be the table name in the SQLite DB
    __tablename__ = 'tasks'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    description = Column(String)
    status = Column(Boolean)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Add Sample Data to the DB - for Testing
add_data = True
if add_data:
    
    # Add Users
    sample_users = [User(first_name='John', last_name='Doe'),
                User(first_name='Jane', last_name='Doe'),
                User(first_name='James', last_name='Doe'),
                User(first_name='Richard', last_name='Roe')]
    session.add_all(sample_users)
    session.commit()
    
    # Add Tasks
    sample_tasks = [Task(description="Learn SQLAlchemy", status=False, user_id=1),
                    Task(description="Back up my DB", status=True, user_id=2),
                    Task(description="Write super awesome Article", status=True, user_id=2),
                    Task(description="Learn Flas", status=False, user_id=1)]
    session.add_all(sample_tasks)
    session.commit()
    
# Delete Sample Data
delete_data = False
if delete_data:
    session.query(User).delete()
    session.commit()
    
    session.query(Task).delete()
    session.commit()
    