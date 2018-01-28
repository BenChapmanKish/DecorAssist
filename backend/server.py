from __future__ import print_function
import flask
import flask_login
from flask_pymongo import PyMongo
from bson.json_util import dumps
import json
import sys

##### RESPONSES #####

responseInvalidLogin = json.dumps({
    'success': False,
    'message': "Your login information was wrong >:("
})

responseNotAuthorized = json.dumps({
    'success': False,
    'message': "You aren't logged in!"
})

responseLoggedOut = json.dumps({
    'success': True,
    'message': "You are now logged out!"
})

responseNoParamsGiven= json.dumps({
    'success':False,
    'message':'Missing a parameter value'
})

responseInvalidUser= json.dumps({
    'success':False,
    'message':'Username is already being used'
})

#####################

app = flask.Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://admin:admin@ds117888.mlab.com:17888/decorate_assistant'
mongo = PyMongo(app)
app.secret_key = 'DecorAssist secret key ;)'

#Database functions

def save_new_user(username,name,password):
    if ( not username or not password or not name):
        return 
    if ( len(list(mongo.db.users.find({'username':username}))) > 0 ):
        return
    try:
        mongo.db.users.insert({'username':username,'name':name,'password':password,'rooms':[]})
        return ({'success':True})
    except:
        return

def get_user_info(username):
    #get user object from mongodb server
    if ( not username ):
        return 
    return (list(mongo.db.users.find({'username':username}))[0])

def update_rooms(username,rooms):
    #gets rooms using username, no return val
    if ( not username ):
        return
    try:
        mongo.db.users.update({'username':username},{'$set':{'rooms':rooms}})
        return
    except:
        return

@app.route('/', methods=['GET','POST'])
def main():
    data = 'test'
    update_rooms('ben',[1,2,3,4])
    ben = get_user_info('ben')
    name = str(ben['name'])
    username = str(ben['username'])
    rooms = list(ben['rooms'])
    print(name,file=sys.stderr)
    print(username,file=sys.stderr)
    print(rooms,file=sys.stderr)
    try:
        return json.dumps(ben)
    except TypeError:
        return dumps(ben)
    
    # if flask.request.method == 'POST':
    #     print()
    #     return json.dumps({'success':True})
    # elif flask.request.method == 'GET':
    #     return json.dumps({'test':'test'})



# Mock database:
users = {  'steven': {'password': 'mypass'},
        'big_poppa': {'password': 'daddy'}}

login_manager = flask_login.LoginManager()

login_manager.init_app(app)

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    if username not in users:
        return

    user = User()
    user.id = username
    return user

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    if username not in users:
        return

    user = User()
    user.id = username

    user.is_authenticated = request.form['password'] == users[username]['password']



@app.route('/login', methods=['POST'])
def login():
    username = flask.request.form['username']
    if flask.request.form['password'] == users[username]['password']:
        user = User()
        user.id = username
        flask_login.login_user(user)
        return flask.redirect(flask.url_for('protected'))

    return responseBadLogin


@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.id

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return responseLoggedOut

@login_manager.unauthorized_handler
def unauthorized_handler():
    return responseNotAuthorized
