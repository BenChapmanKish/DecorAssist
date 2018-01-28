import flask
import flask_login
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson import ObjectId
import json



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
    'message': "You aren't allowed to do that!"
})

responseLoggedOut = json.dumps({
    'success': True,
    'message': "You are now logged out!"
})

responseNoParamsGiven = json.dumps({
    'success': False,
    'message':'Missing a parameter value'
})

responseUsernameTaken = json.dumps({
    'success': False,
    'message':'This username is already in use!'
})

responseErrorCreatingUser = json.dumps({
    'success': False,
    'message':'There was a problem creating your account!'
})

responseErrorCreatingRoom = json.dumps({
    'success': False,
    'message':'There was a problem creating a room!'
})

responseErrorEditingRoom = json.dumps({
    'success': False,
    'message': 'There was a problem editing your room!'
})

#####################

#### Exceptions #####

class userNotFound(Exception):
    pass

class roomNotFound(Exception):
    pass

#####################

# App setup
app = flask.Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://admin:admin@ds117888.mlab.com:17888/decorate_assistant'
mongo = PyMongo(app)
app.secret_key = 'DecorAssist secret key ;)'

def update_user_rooms(username,rooms):
    #gets rooms using username, no return val
    if ( not username ):
        return False
    try:
        mongo.db.users.update_one({'username':username},{'$set':{'rooms':rooms}})
        return True
    except:
        return False


def get_room_info(room_id):
    if (not room_id):
        return None
    response = mongo.db.rooms.find_one({'_id': room_id})
    return response


login_manager = flask_login.LoginManager()

login_manager.init_app(app)

class User(flask_login.UserMixin):
    def __init__(self, username):
        if ( not username ):
            raise userNotFound()
        user = mongo.db.users.find_one({'username':username})
        if not user:
            raise userNotFound()
        self.id        = user['username']
        self.password  = user['password']
        self.name      = user['name']
        self.rooms     = [Room(room) for room in user['rooms']]

class Room():
    def __init__(self, room_id):
        if (not room_id):
            raise roomNotFound()
        room = mongo.db.rooms.find_one({'_id': room_id})
        if not room:
            raise roomNotFound()
        self.id        = room_id
        self.owner     = room['owner']
        self.type      = room['type']
        self.furniture = room['furniture']


@app.route('/')
def main():
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for('homepage'))
    return responseNotLoggedIn



@login_manager.user_loader
def user_loader(username):
    try:
        user = User(username)
    except userNotFound:
        return
    return user

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    try:
        user = User(username)
    except userNotFound:
        return
    user.is_authenticated = request.form['password'] == user.password


@app.route('/signup', methods=['POST'])
def signup():
    try:
        username = flask.request.form['username']
        password = flask.request.form['password']
        name     = flask.request.form['name']
    except:
        return responseInvalidFormEntry

    if ( len(list(mongo.db.users.find({'username':username}))) > 0 ):
        return responseUsernameTaken
    try:
        mongo.db.users.insert({'username':username,'name':name,'password':password,'rooms':[]})
        user = User(username)
        flask_login.login_user(user)
        return flask.redirect(flask.url_for('homepage'))
    except:
        return responseErrorCreatingUser
    



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
    
    try:
        username = flask.request.form['username']
    except:
        return responseInvalidFormEntry

    try:    
        user = User(username)
        if flask.request.form['password'] == user.password:
            flask_login.login_user(user)
            return flask.redirect(flask.url_for('homepage'))
    except:
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
        'rooms': [{
                   'id': str(room.id),
                 'type': room.type,
            'furniture': room.furniture
            } for room in user.rooms]
    })


@app.route('/room/<room_id>')
@flask_login.login_required
def room(room_id):
    if not room_id:
        return responseInvalidFormEntry

    user = flask_login.current_user
    room_id = ObjectId(room_id)

    room = Room(room_id)
    if (room == None or room.owner != user.id):
        return responseNotAuthorized

    return json.dumps({
          'success': True,
               'id': str(room.id),
             'type': room.type,
        'furniture': room.furniture
    })


def get_new_room_id():
    # This is really hacky
    return max(rooms.keys()) + 1
    

@app.route('/new_room', methods=['POST'])
@flask_login.login_required
def new_room():
    owner     = flask_login.current_user.id
    room_type = flask.request.form['type']
    furniture = flask.request.form['furniture']

    if (not owner or not room_type or not furniture):
        return responseInvalidFormEntry
    new_room = { 'owner': owner, 'type': room_type, 'furniture': furniture}
    try:
        room_id = mongo.db.rooms.insert_one({'owner':owner, 'type':room_type, 'furniture':furniture}).inserted_id
        rooms = mongo.db.users.find_one({'username':owner})['rooms']
        rooms.append(room_id)
        mongo.db.users.update_one({'username':owner},{'$set':{'rooms':rooms}})
        return flask.redirect(flask.url_for('room', room_id=room_id))

    except:
        return responseErrorCreatingRoom



@app.route('/edit_room/<room_id>', methods=['POST'])
@flask_login.login_required
def edit_room(room_id):
    if not room_id:
        return responseInvalidFormEntry

    user = flask_login.current_user
    room_id = ObjectId(room_id)
    room = Room(room_id)

    if (room == None or room.owner != user.id):
        return responseNotAuthorized

    room_type = flask.request.form.get('type', None)
    furniture = flask.request.form.get('furniture', 'null')
    try:
        furniture = json.loads(furniture)
    except:
        return responseInvalidFormEntry

    try:
        if room_type:
            mongo.db.rooms.update_one({'_id': room_id}, {'$set': {'type': room_type}})
        if furniture:
            mongo.db.rooms.update_one({'_id': room_id}, {'$set': {'furniture': furniture}})
        return flask.redirect(flask.url_for('room', room_id=room_id))
    except:
        return responseErrorEditingRoom

    
    


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return responseLoggedOut

@login_manager.unauthorized_handler
def unauthorized_handler():
    return responseNotLoggedIn

