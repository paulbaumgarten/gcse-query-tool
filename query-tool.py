"""

GCSE Computer Science "query-by-example" tool.

Purpose: 

    This is intended to replicate the query tool look that is used in the GCSE exams for use with SQLite databases.

Known issues / to-do list:

    * Needs vertical & horizontal scrolling for when dataset requires it.
    * Allow for SQL queries that join multiple tables.

Project repo: 
    
    http://github.com/paulbaumgarten/gcse-query-tool

Author: 

    Paul Baumgarten, November 2020
    http://pbaumgarten.com/igcse-compsci

"""

# Only importing from standard libraries (in order to keep it simple for less experienced programmers to get this to run without the hassle of installing packages)
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from pprint import pprint
import sqlite3
import os

class LocalDatabase:
    """ Helper class to manage the database connection """
    def __init__(self, database_filename):
        self.file_name = database_filename
        self.db_conn = sqlite3.connect( database_filename )
        self.db_conn.row_factory = sqlite3.Row
        self.db = self.db_conn.cursor()
        self.db_open = True
        
    def read(self, sql, filter=None):
        # Query the database and return a list of key:val dicts
        if filter is not None:
            self.db.execute(sql, filter)
        else:
            self.db.execute(sql)
        result = [ dict(row) for row in self.db.fetchall() ]
        return result
    
    def write(self, sql, data=None):
        """
        Example calls using the optional data parameter
        .write("REPLACE INTO table (field1,field2,field3) VALUES (?,?,?);", ["a","b","c"])

        Refer to "parameter substitution" at https://docs.python.org/3.8/library/sqlite3.html
        """
        rows_affected = 0
        if data and isinstance(data, list):
            rows_affected = self.db.execute(sql, data).rowcount
        else:
            rows_affected = self.db.execute(sql).rowcount
        self.db_conn.commit()
        return rows_affected

class App():
    def __init__(self, parent):
        """ App constructor """
        # Create the window
        self.parent = parent
        self.window = tk.Toplevel()
        self.window.geometry("850x600")
        self.window.title("GCSE CompSci Query tool")
        self.window.protocol("WM_DELETE_WINDOW", self.window.quit)
        # Open an SQLite database
        self.open_database()
        # Render screen
        self.render_form()
        # Initialise database query results
        self.results = []

    def open_database(self):
        """ Prompt the user to nominate a database file, open it, and load preliminary data from it """
        # Prompt user for an SQLite database file
        filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Open an SQLite database file")
        # Check dialog wasn't cancelled
        if len(filename) == 0 or not os.path.exists(filename):
            messagebox.showerror("Unable to continue","You must select an existing SQLite database to proceed\nA recommended tool to create one is DB Browser from https://sqlitebrowser.org/")
            exit(1)
        # Check database is valid, and obtain list of tables
        try:
            # Create a database object
            self.db = LocalDatabase(filename)
            # Get tables listing
            tables = self.db.read("SELECT name FROM sqlite_master WHERE type='table';")
        except sqlite3.DatabaseError:
            messagebox.showerror("Unable to continue","Sorry, that file is not a valid SQLite database")
            exit(1)
        # Populate a list of tables for our app
        self.tables = []
        self.fields = []
        for val in tables:
            if "name" in val:
                # Add table name to self.tables list
                self.tables.append(val['name'])
        print("Found tables:",self.tables)
        # Get all fields within each table
        for table in self.tables:
            # Read the first row of every table so we can extract field names
            data = self.db.read(f"SELECT * FROM {table} LIMIT 1;")
            if len(data) == 1: # If the table returned a record
                for key,val in data[0].items():
                    # Add a field record to the self.fields list
                    self.fields.append( {"table": table, "field": key} )
        print("Found fields:",self.fields)
        
    def render_form(self):
        """ Create the query window """
        # Frame to contain fields
        self.container = tk.Frame(self.window)
        self.container.pack()
        self.container.columnconfigure(0, pad=50)
        self.container.rowconfigure(0, pad=50)
        # Labels
        self.labels = [
            tk.Label(self.container, text="Field:", anchor='w'),
            tk.Label(self.container, text="Table:", anchor='w'),
            tk.Label(self.container, text="Sort:", anchor='w'),
            tk.Label(self.container, text="Show:", anchor='w'),
            tk.Label(self.container, text="Criteria:", anchor='w'),
            tk.Label(self.container, text="or:", anchor='w')
        ]
        for i in range(len(self.labels)):
            self.labels[i].grid(column=0, row=i)
        # Execute button
        self.execute_button = tk.Button(self.container, text="Execute", command=self.execute_query)
        self.execute_button.grid(column=0, row=len(self.labels))
        # Lists to hold all the widgets we will be drawing on screen
        self.widgets_field = []
        self.widgets_table = []
        self.widgets_sort = []
        self.widgets_show = []
        self.widgets_criteria = []
        self.widgets_or = []
        # Lists of values for the combobox for fields and tables
        fields_list = [""] + [ x['field'] for x in self.fields ]
        tables_list = [""] + [ x for x in self.tables ]
        # Create a column for every field
        for i in range(len(self.fields)):
            # Field combobox
            self.widgets_field.append( ttk.Combobox(self.container, width=13, values=fields_list) )
            self.widgets_field[-1].grid(row=0, column=i+1)
            self.widgets_field[-1].insert(0, "")
            # Table combobox
            self.widgets_table.append( ttk.Combobox(self.container, width=13, values=tables_list) )
            self.widgets_table[-1].grid(row=1, column=i+1)
            self.widgets_table[-1].insert(0, self.tables[0])
            self.widgets_table[-1].bind("<<ComboboxSelected>>", self.change_of_table)
            # Sort combobox
            self.widgets_sort.append( ttk.Combobox(self.container, width=13, values=["","ASC","DESC"]) )
            self.widgets_sort[-1].grid(row=2, column=i+1)
            # Show checkbox
            self.widgets_show.append( ttk.Checkbutton(self.container) )
            self.widgets_show[-1].state(['!alternate'])
            self.widgets_show[-1].grid(row=3, column=i+1)
            # Criteria entrybox
            self.widgets_criteria.append( tk.Entry(self.container, width=13) )
            self.widgets_criteria[-1].grid(row=4, column=i+1)
            # Or entrybox
            self.widgets_or.append( tk.Entry(self.container, width=13) )
            self.widgets_or[-1].grid(row=5, column=i+1)
        self.widget_query = tk.Label(self.container, width=(13*len(self.fields)), anchor='w')
        self.widget_query.grid(row=6,column=1,columnspan=len(self.fields))

    def change_of_table(self):
        # TO-DO
        pass
    
    def execute_query(self):
        """ Execute the query as provided by the user """
        sql_fields = []
        sql_tables = []
        sql_sort = []
        sql_where = []
        for i in range(len(self.fields)):
            # Full qualified field name
            # TODO - Will need this for table joins - fqfn = "`"+self.widgets_table[i].get() +"."+self.widgets_field[i].get()+"`"
            fqfn = "`"+self.widgets_field[i].get()+"`"
            # If the "show" checkbox is ticked
            if self.widgets_show[i].instate(['selected']):
                # Add field name to SQL
                sql_fields.append(fqfn)
                # Add table name to SQL (if not already added by another field)
                if not self.widgets_table[i].get() in sql_tables:
                    sql_tables.append(self.widgets_table[i].get())
                # If sort order has been specified
                if self.widgets_sort[i].get() in ("ASC","DESC"):
                    sql_sort.append(fqfn + " " + self.widgets_sort[i].get())
            # If a WHERE clause has been specified
            if self.widgets_criteria[i].get() != "":
                sql_where_this = fqfn + self.widgets_criteria[i].get()
                # Only accept an OR clause if the CRITERIA entry box has also been provided
                if self.widgets_or[i].get() != "":
                    sql_where_this += " OR " + fqfn + self.widgets_or[i].get()
                sql_where.append(sql_where_this)
        # Check we were given something to do
        if len(sql_fields) == 0:
            messagebox.showerror("Nothing to do","You haven't asked for any data\n\nCheck you have\n1. Selected a field\n2. Selected the table\n3. Turned on 'show'")
            return
        # Check we aren't trying multiple tables yet
        if len(sql_tables) > 1:
            messagebox.showerror("Opps...","Sorry, multi-table SQL queries not yet available.")
            return
        # Bring the SQL statement all together
        sql = "SELECT " + ",".join(sql_fields) + " FROM " + sql_tables[0]
        if len(sql_where) > 0:
            sql += " WHERE (" + ") AND (".join(sql_where) + ")"
        if len(sql_sort) > 0:
            sql += " ORDER BY " + ",".join(sql_sort)
        print("\nExecuting: "+sql)
        self.widget_query['text'] = sql
        # Execute the query
        data = []
        try:
            data = self.db.read(sql)
            pprint(data)
        except sqlite3.OperationalError:
            messagebox.showerror("SQL Error","Malformed SQL query. Sorry.\n\nThe offending attempted query was:\n"+sql)
        # If we have existing records displayed, we need to clear them!
        if len(self.results) > 0:
            for widget in self.results:
                widget.destroy()
        # If we have data to show
        if len(data) > 0:
            for i in range(len(data)):
                for j in range(len(self.fields)):
                    field_name = self.widgets_field[j].get()
                    if field_name in data[i]:
                        self.results.append( tk.Label(self.container, text=data[i][field_name], borderwidth=1, relief="groove", anchor='w'))
                    else:
                        self.results.append( tk.Label(self.container, text=""))
                    self.results[-1].grid(row=8+i, column=j+1, sticky="nsew")

### MAIN ###
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = App(root)
    root.mainloop()

