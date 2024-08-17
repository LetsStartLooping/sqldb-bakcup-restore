import os
from sqlalchemy import create_engine, MetaData
from helpers import *
    
if __name__ == '__main__':

    # Create a local SQLite DB
    # If DB doesn't exist then it will create it, 
    # else it will just return the `engine` that points to the SQLite DB    
    engine = create_engine('sqlite:///my_sql_db.db', echo=True)
    
    ######## Get Insert and Delete Order ########
    delete_order, insert_order = get_ordered_table_names(engine)
    
    
    ######### Sample code to Back up Table Data ########
    
    # for table_name in get_table_names(engine):
    #     # Get the back-up in the current working directory.
    #     back_up_table(engine, table_name, os.getcwd())
    
    ######### Sample code to Delete Table Data ########
    # delete_table_records(engine, delete_order)
    
    ######### Sample code to Restore Table Data ########
    # restore_table_records(engine, insert_order, os.getcwd())
    