import flask
import flask_login
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

#####################

app = flask.Flask(__name__)
app.secret_key = 'DecorAssist secret key ;)'

@app.route('/', methods=['GET','POST'])
def main():
    data = flask.request.data
    print(data)
    if flask.request.method == 'POST':
        print()
        return json.dumps({'success':True})
    elif flask.request.method == 'GET':
        return json.dumps({'test':'test'})



# Mock database:
users = {
    'steven': {
         'password': 'stevenrulez',
             'name': 'Steven Richards',
        'room_type': 'Living Room'
        },
    'big_poppa': {
         'password': 'callmedaddy',
             'name': 'Big Poppa Sr.',
        'room_type': 'Bedroom'
        }
}

login_manager = flask_login.LoginManager()

login_manager.init_app(app)

class User(flask_login.UserMixin):
    def __init__(self, username):
        self.id = username
        self.password  = users[username]['password']
        self.name      = users[username]['name']
        self.room_type = users[username]['room_type']

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

    return responseBadLogin


@app.route('/homepage')
@flask_login.login_required
def homepage():
    return '<h3>Welcome to DecorAssist, <em>' + flask_login.current_user.name + '</em></h3>'

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return responseLoggedOut

@login_manager.unauthorized_handler
def unauthorized_handler():
    return responseNotAuthorized
