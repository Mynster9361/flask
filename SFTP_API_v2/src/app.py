from fastapi import FastAPI
import pypyodbc as odbc
import datetime

DRIVER_NAME = 'SQL Server'
SERVER_NAME = r'DESKTOP-AGP03A8\MSSQLSERVER01'
DATABASE_NAME = 'fastapi'
connection_string = f"""
    DRIVER={{{DRIVER_NAME}}};
    SERVER={SERVER_NAME};
    DATABASE={DATABASE_NAME};
    Trust_Connection=yes;
"""

app = FastAPI()

@app.get("/to/")
async def list_available_files():
    query = """
    SELECT [id], [filename], [status] 
    FROM [fastapi].[dbo].[to] 
    WHERE status = 'uploaded'
    """
    conn = odbc.connect(connection_string)
    cursor = conn.cursor()
    try:
        # Execute select query
        cursor.execute(query)
        # Fetch all rows as a list of dictionaries
        rows = cursor.fetchall()
        rows = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        return {"files": rows}
    except Exception as e:
        # Handle any exceptions
        print("Error:", e)
        return {"message": "Failed to list available files."}
    finally:
        # Close cursor and connection
        cursor.close()
        conn.close()

@app.get("/to/{id}")
def download_file(id: int):
    query = """
    SELECT [filename], [data] 
    FROM [fastapi].[dbo].[to] 
    WHERE id = ?;
    """
    update_query = """
    UPDATE to
    SET status =  ?
    WHERE id = ?;
    """
    conn = odbc.connect(connection_string)
    cursor = conn.cursor()
    try:
        # Execute select query
        cursor.execute(query, (id,))
        # Fetch all rows as a list of dictionaries
        rows = cursor.fetchall()
        rows = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        try:
            cursor.execute(update_query, ('processed', id))
            conn.commit()
        
        except Exception as e:
            print("Error:", e)
            return {"message": "Failed to update status. Error happend on the server side."}
        
        return {"files": rows}
    
    except Exception as e:
        # Handle any exceptions
        print("Error:", e)
        return {"message": "Failed to get file. Error happend on the client side, check the id."}
    
    finally:
        # Close cursor and connection
        cursor.close()
        conn.close()

@app.post("/to/")
async def create_upload_file(name: str, data: str, ):
    time_now = datetime.datetime.now()
    formatted_time = time_now.strftime('%Y-%m-%d %H:%M:%S')
    query = """
    INSERT INTO to 
    (filename, data, uploaded_at, status) 
    VALUES (?, ?, ?, ?)
    """
    conn = odbc.connect(connection_string)
    cursor = conn.cursor()
    try:
        # Execute insert query
        cursor.execute(query, (name, data, formatted_time, 'uploaded'))
        # Commit changes
        conn.commit()
        print("Query executed successfully!")
        return {"file": name + " uploaded"}
    except Exception as e:
        # Handle any exceptions
        print("Error:", e)
        return {"file": name + " not uploaded"}
    finally:
        # Close cursor and connection
        cursor.close()
        conn.close()


@app.get("/from/")
async def list_available_files():
    query = """
    SELECT [id], [filename], [status] 
    FROM [fastapi].[dbo].[from] 
    WHERE status = 'uploaded'
    """
    conn = odbc.connect(connection_string)
    cursor = conn.cursor()
    try:
        # Execute select query
        cursor.execute(query)
        # Fetch all rows as a list of dictionaries
        rows = cursor.fetchall()
        rows = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        return {"files": rows}
    except Exception as e:
        # Handle any exceptions
        print("Error:", e)
        return {"message": "Failed to list available files."}
    finally:
        # Close cursor and connection
        cursor.close()
        conn.close()

@app.get("/from/{id}")
def download_file(id: int):
    query = """
    SELECT [id], [data], [status] 
    FROM [fastapi].[dbo].[from] 
    WHERE id = ?;
    """
    update_query = """
    UPDATE from
    SET status = ?
    WHERE id = ?;
    """
    conn = odbc.connect(connection_string)
    cursor = conn.cursor()
    try:
        # Execute select query
        cursor.execute(query, (id,))
        # Fetch all rows as a list of dictionaries
        rows = cursor.fetchall()
        rows = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        try:
            cursor.execute(update_query, ('processed', id))
            conn.commit()
        except Exception as e:
            print("Error:", e)
            return {"message": "Failed to update file. Error happend on the server"}
        return {"files": rows}
    except Exception as e:
        # Handle any exceptions
        print("Error:", e)
        return {"message": "Failed to get file. Error happend on the client side, check the id."}
    finally:
        # Close cursor and connection
        cursor.close()
        conn.close()

@app.post("/from/")
async def create_upload_file(name: str, data: str, ):
    time_now = datetime.datetime.now()
    formatted_time = time_now.strftime('%Y-%m-%d %H:%M:%S')
    query = """
    INSERT INTO from
    (filename, data, uploaded_at, status) 
    VALUES (?, ?, ?, ?)
    """
    conn = odbc.connect(connection_string)
    cursor = conn.cursor()
    try:
        # Execute insert query
        cursor.execute(query, (name, data, formatted_time, 'uploaded'))
        # Commit changes
        conn.commit()
        print("Query executed successfully!")
        return {"file": name + " uploaded"}
    except Exception as e:
        # Handle any exceptions
        print("Error:", e)
        return {"file": name + " not uploaded"}
    finally:
        # Close cursor and connection
        cursor.close()
        conn.close()

