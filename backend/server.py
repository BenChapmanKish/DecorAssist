import flask
import flask_login
from flask_pymongo import PyMongo
from bson.json_util import dumps
import json
import sys

##### RESPONSES #####

responseNotLoggedIn = json.dumps({
    'success': False,
    'message': "You aren't logged in! Login or sign up now!"
})

responseInvalidLogin = json.dumps({
    'success': False,
    'message': "Your login information was wrong >:("
})

responseInvalidRoom  = json.dumps({
    'success': False,
    'message': "This room doesn't exist!"
})

responseInvalidFormEntry = json.dumps({
    'success': False,
    'message': "You didn't send the form data correctly!"
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

#@app.route('/', methods=['GET','POST'])
#def main():
#    data = 'test'
#    update_rooms('ben',[1,2,3,4])
#    ben = get_user_info('ben')
#    name = str(ben['name'])
#    username = str(ben['username'])
#    rooms = list(ben['rooms'])
#    print(name,file=sys.stderr)
#    print(username,file=sys.stderr)
#    print(rooms,file=sys.stderr)
#    try:
#        return json.dumps(ben)
#    except TypeError:
#        return dumps(ben)
    
    # if flask.request.method == 'POST':
    #     print()
    #     return json.dumps({'success':True})
    # elif flask.request.method == 'GET':
    #     return json.dumps({'test':'test'})



# Mock database:
users = {
    'steven': {
         'password': 'stevenrulez',
             'name': 'Steven Richards',
            'rooms': [1],
        },
    'big_poppa': {
         'password': 'callmedaddy',
             'name': 'Big Poppa Sr.',
            'rooms': [2]
        }
}

rooms = {
    1: {
            'owner': 'steven',
             'type': 'living_room',
        'furniture': ['chair', 'couch', 'lamp', 'plant', 'tv']
    },
    2: {
            'owner': 'big_poppa',
             'type': 'bedroom',
        'furniture': ['bed', 'table', 'lamp', 'dresser', 'art']
    }
}

login_manager = flask_login.LoginManager()

login_manager.init_app(app)

class User(flask_login.UserMixin):
    def __init__(self, username):
        self.id = username
        self.password  = users[username]['password']
        self.name      = users[username]['name']
        self.rooms     = [Room(room) for room in users[username]['rooms']]

class Room():
    def __init__(self, room_id):
        self.id        = room_id
        self.owner     = rooms[room_id]['owner']
        self.type      = rooms[room_id]['type']
        self.furniture = rooms[room_id]['furniture']


@app.route('/')
def main():
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for('homepage'))
    return responseNotLoggedIn



@login_manager.user_loader
def user_loader(username):
    if username not in users:
        return

    user = User(username)
    return user

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    if username not in users:
        return

    user = User(username)
    user.is_authenticated = request.form['password'] == user.password


@app.route('/signup', methods=['POST'])
def signup():
    try:
        username = flask.request.form['username']
        users[username] = {
            'password': flask.request.form['password'],
            'name': flask.request.form['name'],
            'rooms': []
        }
    except:
        return responseInvalidFormEntry

    user = User(username)
    flask_login.login_user(user)
    return flask.redirect(flask.url_for('homepage'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='username' id='username' placeholder='username'/>
                <input type='password' name='password' id='password' placeholder='password'/>
                <input type='submit' name='submit'/>
               </form>
               '''
    
    username = flask.request.form['username']
    user = User(username)
    if flask.request.form['password'] == user.password:
        flask_login.login_user(user)
        return flask.redirect(flask.url_for('homepage'))

    return responseInvalidLogin


@app.route('/homepage')
@flask_login.login_required
def homepage():
    user = flask_login.current_user
    return json.dumps({
        'success': True,
        'user': {
            'username': user.id,
            'name': user.name,
        },
        'rooms': [room.id for room in user.rooms]
    })


@app.route('/room/<room_id>')
@flask_login.login_required
def room(room_id):
    room_id = int(room_id)
    if room_id not in rooms:
        return responseInvalidRoom

    room = Room(room_id)
    return json.dumps({
          'success': True,
             'type': room.type,
        'furniture': room.furniture
    })


def get_new_room_id():
    # This is really hacky
    return max(rooms.keys()) + 1
    

@app.route('/new_room', methods=['POST'])
@flask_login.login_required
def new_room():
    user = flask_login.current_user
    room_id = get_new_room_id()
    try:
        rooms[room_id] = {
            'owner': user.id,
            'type': flask.request.form['type'],
            'furniture': flask.request.form['furniture'],
        }
    except:
        return responseInvalidFormEntry

    return flask.redirect(flask.url_for('room', room_id=room_id))

@app.route('/logout', methods=['POST'])
def logout():
    flask_login.logout_user()
    return responseLoggedOut

@login_manager.unauthorized_handler
def unauthorized_handler():
    return responseNotAuthorized
