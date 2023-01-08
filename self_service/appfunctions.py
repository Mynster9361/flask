import json
import jwt
import mysql.connector
import app_config

def get_users_roles(session):
    id_token = session['token_cache']
    data = json.loads(id_token)
    id_token = data["IdToken"]
    user_token = next(iter(id_token.items()))[1]['secret']
    decoded_token = jwt.decode(user_token, algorithms=['RS256'], options={"verify_signature": False})
    if 'roles' in decoded_token:
        # obj has an attribute called 'roles'
        roles = decoded_token['roles']
    else:
        # obj does not have an attribute called 'roles'
        roles = []
    return roles

def mysql_create(self_service_name, self_service_description, self_service_Access, self_service_Runbook, self_service_selfserviceaction, usersemail):
    # Connect to the database
    conn = mysql.connector.connect(
        host=app_config.SQL_HOST,
        user=app_config.SQL_USER,
        password=app_config.SQL_PASSWORD,
        database=app_config.SQL_DB
    )

    # Create a cursor to execute SQL commands
    cursor = conn.cursor()

    # Insert a new self service
    approved = 0 # 0 = FALSE 1 = TRUE
    cursor.execute(
        "INSERT INTO self_services_draft (name, description, access, runbook, actions, approved, createdby) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (self_service_name, self_service_description, self_service_Access, self_service_Runbook, self_service_selfserviceaction, approved, usersemail)
    )

    # Commit the changes to the database
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()

def mysql_view_draft():
    # Connect to the database
    conn = mysql.connector.connect(
        host=app_config.SQL_HOST,
        user=app_config.SQL_USER,
        password=app_config.SQL_PASSWORD,
        database=app_config.SQL_DB
    )

    # Create a cursor to execute SQL commands
    cursor = conn.cursor()

    # Insert a new self service
    cursor.execute(
        "SELECT * FROM self_services_draft;"
    )

    # Fetch the results of the query
    result = cursor.fetchall()

    # Commit the changes to the database
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()
    return result

def mysql_view():
    # Connect to the database
    conn = mysql.connector.connect(
        host=app_config.SQL_HOST,
        user=app_config.SQL_USER,
        password=app_config.SQL_PASSWORD,
        database=app_config.SQL_DB
    )

    # Create a cursor to execute SQL commands
    cursor = conn.cursor()

    # Insert a new self service
    cursor.execute(
        "SELECT * FROM self_services;"
    )

    # Fetch the results of the query
    result = cursor.fetchall()

    # Commit the changes to the database
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()
    return result

def mysql_view_id(id):
       
    # Connect to the database
    conn = mysql.connector.connect(
        host=app_config.SQL_HOST,
        user=app_config.SQL_USER,
        password=app_config.SQL_PASSWORD,
        database=app_config.SQL_DB
    )

    # Create a cursor to execute SQL commands
    cursor = conn.cursor()

    # Insert a new self service
    cursor.execute(
        "SELECT * FROM self_services WHERE id = {id};"
    )

    # Fetch the results of the query
    result = cursor.fetchall()

    # Commit the changes to the database
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()
    return result

def mysql_view_draftid(id):
    # Connect to the database
    conn = mysql.connector.connect(
        host=app_config.SQL_HOST,
        user=app_config.SQL_USER,
        password=app_config.SQL_PASSWORD,
        database=app_config.SQL_DB
    )

    # Create a cursor to execute SQL commands
    cursor = conn.cursor()

    # Insert a new self service
    cursor.execute(
        "SELECT * FROM self_services_draft WHERE id = %s;", (id,)
    )

    # Fetch the results of the query
    result = cursor.fetchall()

    # Commit the changes to the database
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()
    return result
