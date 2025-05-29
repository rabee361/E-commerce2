import sqlite3
import mysql.connector
from mysql.connector import connection_cext

def extend_cursor_factory(sqlconnector):
    if str(type(sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
        # Check if we're using the C extension version or pure Python
        if hasattr(mysql.connector, 'connection_cext') and hasattr(connection_cext, 'CMySQLCursor'):
            base_cursor = connection_cext.CMySQLCursor
        else:
            base_cursor = mysql.connector.cursor.MySQLCursor
    elif str(type(sqlconnector)) == "<class 'SqliteConnector.SqliteConnector'>":
        base_cursor = sqlite3.Cursor
    else:
        raise ValueError("Unsupported database type")

    class ExtendedCursor(base_cursor):
        """
        TLDR; extend_cursor_factory creates an ExtendedCursor class that extends either MySQLCursor or sqlite3.Cursor 
        to allow flexible result formats with mixed index/column name access.
        """

        """
        extend_cursor_factory is a factory function that creates a custom cursor class extending either 
        MySQLCursor or sqlite3.Cursor based on the provided sqlconnector type.

        The returned ExtendedCursor class provides additional functionality:
        - Flexible row access using both numeric indices and column names
        - Configurable index_type parameter to control result format:
          - 'mixed': Access via both indices and column names (default)
          - 'numeric': Access via numeric indices only 
          - 'columns_names': Access via column names only
        - Compatible with both MySQL and SQLite databases

        Methods:
        - execute(query, params=None): Executes the given query with optional parameters
        - fetchone(): Fetches a single row as a dictionary with configured access format
        - fetchall(): Fetches all rows as list of dictionaries with configured access format

        Example usage:
        ```python
        from ExtendedCursor import extend_cursor_factory
        
        # Create cursor class for your connector type
        ExtendedCursor = extend_cursor_factory(mysql_connector)
        
        # Use the cursor with your connection
        cursor = conn.cursor(cursor_class=ExtendedCursor, index_type='mixed')
        
        cursor.execute("SELECT id, name FROM users")
        row = cursor.fetchone()
        
        # Access by index or column name
        user_id = row[0]  # or row['id']
        name = row[1]     # or row['name']
        ```
        """
        def __init__(self, *args, index_type='mixed', **kwargs):
            super().__init__(*args, **kwargs)
            self.index_type = index_type

        def execute(self, query, params=None):
            super().execute(query) if params is None else super().execute(query, params)
            # Set column names after executing a query in SQLite Connections
            if isinstance(self, sqlite3.Cursor) and self.description:
                self.column_names = [desc[0] for desc in self.description]

        def fetchone(self):
            row = super().fetchone()
            if row:
                if self.index_type == 'mixed':
                    row_dict = {**{i: value for i, value in enumerate(row)}, **dict(zip(self.column_names, row))}
                elif self.index_type == 'numeric':
                    row_dict = {i: value for i, value in enumerate(row)}
                elif self.index_type == 'columns_names':
                    row_dict = dict(zip(self.column_names, row))
                else:
                    row_dict = None
                return row_dict
            return None

        def fetchall(self):
            results = super().fetchall()
            row_dicts = []
            for row in results:
                if self.index_type == 'mixed':
                    row_dict = {**{i: value for i, value in enumerate(row)}, **dict(zip(self.column_names, row))}
                elif self.index_type == 'numeric':
                    row_dict = {i: value for i, value in enumerate(row)}
                elif self.index_type == 'columns_names':
                    row_dict = dict(zip(self.column_names, row))
                else:
                    row_dict = None
                if row_dict is not None:
                    row_dicts.append(row_dict)
            return row_dicts
        
    return ExtendedCursor