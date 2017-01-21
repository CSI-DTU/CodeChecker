import os
from dbutil import *
import flask
import flask_login
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, IntegerField
from flask.ext.codemirror.fields import CodeMirrorField
from flask.ext.codemirror import CodeMirror
from hackerrank.HackerRankAPI import HackerRankAPI
from datetime import datetime

CODEMIRROR_LANGUAGES = ['python', 'html']
CODEMIRROR_THEME = 'base16-light'

compiler = HackerRankAPI(api_key = 'hackerrank|751319-994|d057e21968795c38201ca37d376201eff936f29b')


# initialize flask app
app = flask.Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

# codemirror app
codemirror = CodeMirror(app)

class CodeForm(Form):
    source_code = CodeMirrorField(language='python', config={'lineNumbers' : 'true'})
    submit = SubmitField('Submit')


#------------------------ LOGIN FUNCIONALITY ----------------------------------#

# initialize login manager
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
users = fetch_valid_users()

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
        return None

    user = User()
    user.id = username
    user.is_authenticated = request.form['password'] == users[username]['pw']

    return user


@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if flask.request.method == 'GET':
        if flask_login.current_user.get_id() != None:
            return flask.redirect(flask.url_for('home_page'))
        else:
            return flask.render_template('login.html')

    error = ""
    username = flask.request.form['username']

    if username not in users:
        return flask.render_template('login.html', error = "User does not exist!")

    
    if flask.request.form['pass'] != users[username]['pw']:
        return flask.render_template('login.html', error = "Wrong password!")
    
    user = User()
    user.id = username
    flask_login.login_user(user)
    return flask.redirect(flask.url_for('home_page'))


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('home_page'))


@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'

#------------------------------------------------------------------------------#

# Code checker
def check_code(problem, code):
    code = code.lstrip()
    if code == None or code == "":
        return "Fail"
    
    testcase = problem['input']
    output = compiler.run({'lang':'python',
                           'testcases':[testcase],
                           'source':code}).output[0]

    if output[-1] == '\n':
        output = output[:-1]
    
    if output == problem['output']:
        return "Pass"
    else:
        return "Fail"


#------------------------------------------------------------------------------#

@app.route('/problems')
@flask_login.login_required
def show_problems():
    problems = fetch_all_problems()
    return flask.render_template('problems.html', problems = problems)



@app.route('/scoreboard')
@flask_login.login_required
def scoreboard():
    problems = fetch_all_problems()
    headers = ["Rank", "Name", "Score"]
    headers.extend([p.values()[1] for p in problems])

    scoreboard = fetch_scoreboard()
    return flask.render_template('scoreboard.html', headers = headers, scoreboard = scoreboard)
    


@app.route('/start_contest')
@flask_login.login_required
def start_contest():
    username = flask_login.current_user.id

    # invalid user
    if username != "Nikhil":
        return "You are not authorized to access this page!"
    
    time = datetime.now()
    with open("contest_clock.txt",'w') as f:
        f.write(str(time))
    initialize_scoreboard()
    return "Contest clock set at %s"%(str(time))



@app.route('/')
def home_page():
    valid_user = False
    if flask_login.current_user.get_id() != None:
        valid_user = True
    return flask.render_template('index.html', valid_user = valid_user)



@app.route('/problem/<int:problem_id>',methods=['GET', 'POST'])
@flask_login.login_required
def problem_page(problem_id):
    username = flask_login.current_user.id
    problem = fetch_problem(problem_id)
    form = CodeForm(flask.request.form)
    result = None

    if flask.request.method == "POST":
        if form.validate():
            code = flask.request.form['source_code']
            result = check_code(problem, code)

            update_score(username, problem_id, result)

    problem['descr'] = problem['descr'].replace("\n","<br />")
            
    return flask.render_template('editor.html',
                                 form = form,
                                 problem = problem,
                                 result= result)






if __name__ == "__main__":
    app.run(debug = True, port = 5050)
