from flask import Flask, render_template, request, redirect, url_for, session
import jira

app = Flask(__name__)
app.secret_key = 'secret_key'

# JIRA API credentials
jira_url = 'https://your-jira-instance.com'
jira_username = 'your_username'
jira_password = 'your_password'

# Connect to JIRA API
#jira_client = jira.JIRA(jira_url, basic_auth=(jira_username, jira_password))

@app.route('/')
def home():
    # Display home page with login/logout button
    logged_in = 'username' in session
    return render_template('home.html', logged_in=logged_in)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Authenticate user and set session variables
        email = request.form['email']
        password = request.form['password']
        if authenticate(email, password):
            session['username'] = email
            session['permissions'] = get_permissions(email)
            return redirect(url_for('self_service'))
        # If authentication fails, redirect to login page
        return redirect(url_for('login'))
    else:
        # Display login page for GET requests
        return render_template('login.html')


@app.route('/logout')
def logout():
    # Clear session variables
    session.clear()
    return redirect(url_for('home'))

@app.route('/self-service')
def self_service():
    # Get the search query from the request arguments
    query = request.args.get('query')

    # Filter the self-service options based on the search query
    services = get_services(session['permissions'])
    if query:
        services = [s for s in services if query.lower() in s.name.lower()]

    # Display list of self-service options available to the user
    return render_template('self_service.html', services=services)

@app.route('/request/<service_id>', methods=['POST'])
def request_service(service_id):
    # Create new self-service request
    requester = session['username']
    approver = get_approver(service_id)
    create_request(requester, approver, service_id)
    return redirect(url_for('status'))

@app.route('/status')
def status():
    # Display list of previous self-service requests and their current status
    requests = get_requests(session['username'])
    return render_template('status.html', requests=requests)

@app.route('/suggestions', methods=['GET', 'POST'])
def suggestions():
    if request.method == 'POST':
        # Create new JIRA issue for suggestion or request
        summary = request.form['summary']
        description = request.form['description']
        jira_client.create_issue(project='SELF', summary=summary, description=description)
        return redirect(url_for('suggestions'))
    # Display form for suggesting changes or requesting new self-service options
    return render_template('suggestions.html')

@app.route('/admin')
def admin():
    # Check if user has admin permission
    if 'permissions' not in session or 'admin' not in session['permissions']:
        return redirect(url_for('home'))

    # Display page for creating and modifying self-service options
    services = get_services(session['permissions'])
    return render_template('admin.html', services=services)

@app.route('/create', methods=['POST'])
def create_service():
    # Create new self-service option
    name = request.form['name']
    description = request.form['description']
    flow = request.form['flow']
    create_service(name, description, flow)
    return redirect(url_for('admin'))

@app.route('/modify/<service_id>', methods=['POST'])
def modify_service(service_id):
    # Modify existing self-service option
    name = request.form['name']
    description = request.form['description']
    flow = request.form['flow']
    modify_service(service_id, name, description, flow)
    return redirect(url_for('admin'))

def authenticate(username, password):
    # Check if username and password are valid
    return True

def get_permissions(username):
    # Return list of permissions for a given user
    return ['self_service', 'suggestions']

class SelfServiceOption:
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description
        
def get_services(permissions):
    # Create a list of self-service option objects
    services = []

    # Add self-service options to the list
    services.append(SelfServiceOption(id=1, name='Access to AD Group', description='Request access to an AD group'))
    services.append(SelfServiceOption(id=2, name='Software Install', description='Request installation of software on your device'))

    # Return list of self-service options available to the user
    return services

def get_approver(service_id):
    # Return approver for a given self-service option
    return 'manager'

def create_request(requester, approver, service_id):
    # Create new self-service request
    pass

def get_requests(requester):
    # Return list of previous self-service requests for a given user
    return [{'id': 1, 'service': 'Access to AD Group', 'status': 'Pending'}, {'id': 2, 'service': 'Software Install', 'status': 'Approved'}]

def create_service(name, description, flow):
    # Create new self-service option
    pass

def modify_service(service_id, name, description, flow):
    # Modify existing self-service option
    pass

if __name__ == '__main__':
    app.run()