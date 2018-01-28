from __future__ import print_function
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
