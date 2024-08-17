import pandas as pd
import os

from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base

# Incase you don't want to take back up of certain tables, you can put in this list. 
# Else leave this list blank
exclude_tables = ['alembic_version']

# Back up a single DB Table
def back_up_table(engine, table_name, path):
    '''
    Back up a DB table into a CSV file
    - Input Parameters:
        - engine: SQL Engine, can be created via `create_engine` from `sqlalchemy`
        - table_name: Name of the table to be backed up
        - path: path of the Folder where backup CSV file will be stored
        
    CSV file will have the same name as the name of the table
    '''
    # Read the table into a pandas DataFrame
    # This is standard pandas method `read_sql_table`
    df = pd.read_sql_table(table_name, engine)
    
    # Write the DataFrame to a CSV file
    df.to_csv(os.path.join(path, f"{table_name}.csv"), index=False)
    
    # Output message
    print(f"Backup Successfully created for Table: {table_name}")
    
# Delete Records from a single table    
def delete_table_records(engine, table_names):
    
    # Get the back-up in the current working directory.
    for table_name in table_names:
        back_up_table(engine, table_name, os.getcwd())
    
    # Create a Session to interact with the DB
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Generate ORM Classes out of DB table structures
    Base = automap_base()
    Base.prepare(autoload_with=engine)

    for table_name in table_names:
        # Get table class
        table = Base.classes[table_name]

        # Delete table records
        session.query(table).delete()
        session.commit()
        
# Restore Table Records
def restore_table_records(engine, table_names, path):
    
    # Create a Session to interact with the DB
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Generate ORM Classes out of DB table structures
    Base = automap_base()
    Base.prepare(autoload_with=engine)
    
    for table_name in table_names:
        
        # Combine Folder path and file name based on table name
        file_path = os.path.join(path, f"{table_name}.csv")
        
        # Read CSV into a DataFrame
        df = pd.read_csv(file_path)
        df = df.fillna("")
        
        print(f"Inserting Records in the table {table_name}")
        
        # Get table Class 
        table = Base.classes[table_name]
        
        # Create list of records for each row in the CSV file
        records = [table(**row.to_dict()) for index, row in df.iterrows()]
        
        # Insert records into the table
        session.add_all(records)
        
    session.commit()
    
def get_table_names(engine):
    '''
    Returns Table Names in the DB
    - Input Parameters:
        - engine: SQL Engine, can be created via `create_engine` from `sqlalchemy`

    - Returns:
        - table_names: List of name of the tables in the DB
    '''
    
    # Get Metadata of the tables in the DB including their relationships
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    # Get table names
    table_names = [table.name for table in metadata.sorted_tables]    
    
    return table_names
    
def get_ordered_table_names(engine):
    '''
    Get Table names in the DB, in order of their dependencies to each other
    - Parameters:
        - engine: SQL Engine, can be created via `create_engine` from `sqlalchemy`
    
    - Return:
        - delete_order: The order in which data can be deleted from all tables
        - insert_order: The order in which data can be inserted into tables
    '''
    
    # Get Metadata of the tables in the DB including their relationships
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    # Get table names
    table_names = [table.name for table in metadata.sorted_tables if table.name not in exclude_tables]
    
    # Find dependency and build a dependency graph.
    # Dictionary to hold dependent tables
    dependency_graph = {table: set() for table in table_names}
    
    for table in metadata.sorted_tables:
        for foreign_key in table.foreign_keys:
            dependency_graph[table.name].add(foreign_key.column.table.name)
                
    # Topological sort to find the order based on dependencies
    visited = set()
    final_order = []
    
    # Using Depth First Search
    def dfs(table):
        
        # Visit each table once
        if table not in visited:
            
            # Add to visited tables
            visited.add(table)
            
            # Go through each dependent table from the dependency grapch created earlier
            for neighbor in dependency_graph.get(table, []):
                
                # Repeat for each dependent table found in the grapch
                dfs(neighbor)
                
            # Append to final order
            final_order.append(table)
            
    # Perform DFS for each table
    for table in dependency_graph:
        dfs(table)
            
    # Deletion Order
    delete_order = final_order[::-1]
    insert_order = final_order
    
    return delete_order, insert_order
    