import uuid
import requests
from flask import Flask, render_template, session, request, redirect, url_for
from flask_session import Session  # https://pythonhosted.org/Flask-Session
import msal
import app_config
from appfunctions import get_users_roles, mysql_create, mysql_view, mysql_view_id, mysql_view_draft, mysql_view_draftid
import mysql.connector

app = Flask(__name__)
app.config.from_object(app_config)
Session(app)

# This section is needed for url_for("foo", _external=True) to automatically
# generate http scheme when this sample is running on localhost,
# and to generate https scheme when it is deployed behind reversed proxy.
# See also https://flask.palletsprojects.com/en/1.0.x/deploying/wsgi-standalone/#proxy-setups
from werkzeug.middleware.proxy_fix import ProxyFix

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


@app.route("/")
def index():
    if not session.get("user"):
        return redirect(url_for("login"))
    roles = get_users_roles(session=session)
    return render_template('index.html', user=session["user"], roles=roles)

@app.route("/login")
def login():
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    session["flow"] = _build_auth_code_flow(scopes=app_config.SCOPE)
    redirecturlauthflow = auth_url=session["flow"]["auth_uri"]
    #return render_template("login.html", auth_url=session["flow"]["auth_uri"], version=msal.__version__)
    return redirect(redirecturlauthflow)


@app.route(app_config.REDIRECT_PATH)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        app_config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("index", _external=True))

def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()

def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID, authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET, token_cache=cache)

def _build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("authorized", _external=True))

def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result
    
@app.route('/selfservice')
def self_service_options():
    if not session.get("user"):
        return redirect(url_for("login"))
    roles = get_users_roles(session=session)
    # Connect to the database and retrieve the list of services
    services = mysql_view()
    # Initialize an empty list to store the rendered HTML for each service
    service_html = []
    
    # Iterate over the list of services
    for service in services:
        service_id = "selfservice/" + str(service[0])
        service_name = service[1]
        service_description = service[2]
        service_image_url = '/static/img/Sample_User_Icon.png'
        # Render the HTML template for the service and append it to the list
        service_html.append(render_template('service_card.html', name=service_name, description=service_description, id=service_id, image=service_image_url))
        # Render the main HTML template and pass in the list of rendered service HTML
    
    return render_template('selfservice.html', roles=roles, service_html=service_html, header='Self Services')

@app.route("/create_selfservice")
def create_selfservice():
    if not session.get("user"):
        return redirect(url_for("login"))
    roles = get_users_roles(session=session)
    if "Self_Service_Admins" not in roles:
        # Redirect the user to an error page or display an error message
        return redirect(url_for("unauthorized"))
    # Reset the data_inserted flag variable
    global data_inserted
    data_inserted = False
    return render_template("create_selfservice.html", user=session["user"], roles=roles)

@app.route("/draft_selfservice")
def self_service_draft():
    if not session.get("user"):
        return redirect(url_for("login"))
    roles = get_users_roles(session=session)
    # Connect to the database and retrieve the list of services
    services = mysql_view_draft()

    # Initialize an empty list to store the rendered HTML for each service
    service_html = []
    
    # Iterate over the list of services
    for service in services:
        service_id = "draft_selfservice/" + str(service[0])
        service_name = service[1]
        service_description = service[2]
        service_image_url = '/static/img/Sample_User_Icon.png'
        # Render the HTML template for the service and append it to the list
        service_html.append(render_template('service_card.html', name=service_name, description=service_description, id=service_id, image=service_image_url))
        # Render the main HTML template and pass in the list of rendered service HTML
    
    return render_template('selfservice.html', roles=roles, service_html=service_html, header='Self Services drafts')

@app.route("/draft_selfservice/<service_id>")
def self_service_draft_id(service_id):
    if not session.get("user"):
        return redirect(url_for("login"))
    roles = get_users_roles(session=session)
    # Connect to the database and retrieve the list of services

    service = mysql_view_draftid(service_id)
    print(type(service))
    service_name = service[0][1]
    service_description = service[0][2]
    service_accessto = service[0][3]
    service_runbookname = service[0][4]
    service_actions = service[0][5]
    service_approved = service[0][6]
    service_created = service[0][7]
    service_html = ''
    for action in service_actions.split('\n'):
        #print(action)
        print('___________')
        list = action.split(':')
        for element in list:
            print(element)
            key, value = element.split('=')[0], element.split('=')[1]
            print('___________')
            print(key)
            print(value)
            print('___________')
    
    #print(service_actions.split('\n')[0])
    #print(service_actions.split('\n')[1])
    #print(service_actions.split('\n')[2])
    # Render the service template with the service data
    return render_template('view_draft.html', name=service_name, description=service_description, service_actions=service_actions)

@app.route("/modify_selfservice")
def modify_selfservice():
    if not session.get("user"):
        return redirect(url_for("login"))
    roles = get_users_roles(session=session)
    if "Self_Service_Admins" not in roles:
        # Redirect the user to an error page or display an error message
        return redirect(url_for("unauthorized"))
    roles = get_users_roles(session=session)
    # Connect to the database and retrieve the list of services
    services = mysql_view()

    # Initialize an empty list to store the rendered HTML for each service
    service_html = []
    
    # Iterate over the list of services
    for service in services:
        service_id = "modify_selfservice/" + str(service[0])
        service_name = service[1]
        service_description = service[2]
        service_image_url = '/static/img/Sample_User_Icon.png'
        # Render the HTML template for the service and append it to the list
        service_html.append(render_template('service_card.html', name=service_name, description=service_description, id=service_id, image=service_image_url))
        # Render the main HTML template and pass in the list of rendered service HTML
    
    return render_template('selfservice.html', roles=roles, service_html=service_html, header='Please select the self service you would like to modify')

@app.route('/submit', methods=['POST'])
def submit_suggestion():
    if not session.get("user"):
        return redirect(url_for("login"))
    suggestion = request.form.get('suggestion')
    # Save the suggestion to a database or file here
    roles = get_users_roles(session=session)
    return render_template('submit_suggestion.html', roles=roles)


# Set the flag variable to False initially
data_inserted = False
@app.route('/submitselfservice', methods=['POST'])
def submitselfservice():
    # do something with my_variable
    if not session.get("user"):
        return redirect(url_for("login"))
    # Save the suggestion to a database or file here
    roles = get_users_roles(session=session)
    self_service_name = request.form['SelfServiceName']
    self_service_description = request.form['description']
    self_service_Access = request.form['AccessTo']
    self_service_Runbook = request.form['Runbook']
    self_service_selfserviceaction = request.form['selfserviceaction']
    usersemail = session.get("user").get("preferred_username")
    # Declare the data_inserted variable as global
    global data_inserted
    # Check if the data has already been inserted
    if not data_inserted:
        # Connect to the database and input the new self service draft
        mysql_create(self_service_name, self_service_description, self_service_Access, self_service_Runbook, self_service_selfserviceaction, usersemail)
        # Set the flag variable to True
        data_inserted = True

    return render_template('submitselfservice.html', roles=roles, self_service_name=self_service_name)

@app.route('/suggestions')
def view_suggestions():
    if not session.get("user"):
        return redirect(url_for("login"))
    # Retrieve the suggestions from the database or file here
    roles = get_users_roles(session=session)
    return render_template('suggestions.html', roles=roles) #, suggestions=suggestions

class Request:
    def __init__(self, id, subject, status):
        self.id = id
        self.subject = subject
        self.status = status

@app.route("/status")
def status():
    if not session.get("user"):
        return redirect(url_for("login"))
    requests = [
        Request(123, "this is a test to show how it could look", "In progress"),
        Request(456, "this is another test", "Completed"),
    ]
    roles = get_users_roles(session=session)
    return render_template("status.html", items=requests, roles=roles)

@app.route("/admin")
def admin():
    if not session.get("user"):
        return redirect(url_for("login"))
    roles = get_users_roles(session=session)
    if "Self_Service_Admins" not in roles:
        # Redirect the user to an error page or display an error message
        return redirect(url_for("unauthorized"))
    return render_template("admin.html", user=session["user"], roles=roles)

@app.route("/unauthorized")
def unauthorized():
    if not session.get("user"):
        return redirect(url_for("login"))
    roles = get_users_roles(session=session)
    return render_template("unauthorized.html", user=session["user"], roles=roles)
        
@app.route('/selfservice/<int:self_service_id>')
def self_service_show(self_service_id):
    if not session.get("user"):
        return redirect(url_for("login"))
    roles = get_users_roles(session=session)
    # Connect to the database and retrieve the list of services
    services = mysql_view_id(self_service_id)
    #! TODO after new self service template/creation is in place look into the page showing the self service sample code is added here.
    # Initialize an empty list to store the rendered HTML for each service
    service_html = []
    
    # Iterate over the list of services
    for service in services:
        service_id = service[0]
        service_name = service[1]
        service_description = service[2]
        service_image_url = '/static/img/Sample_User_Icon.png'
        # Render the HTML template for the service and append it to the list
        service_html.append(render_template('service_card.html', name=service_name, description=service_description, id=service_id, image=service_image_url))
        # Render the main HTML template and pass in the list of rendered service HTML
    
    return render_template('selfservice.html', roles=roles, service_html=service_html)

app.jinja_env.globals.update(_build_auth_code_flow=_build_auth_code_flow)  # Used in template

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)

