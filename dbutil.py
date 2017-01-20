import sqlite3
from datetime import datetime


conn = sqlite3.connect('codechecker.db', check_same_thread=False)
c = conn.cursor()

pcols = ['id', 'name', 'descr', 'tlimit', 'input', 'output']


def create_scoreboard():
    c.execute("SELECT name FROM users")
    users = c.fetchall()

    c.execute("SELECT name FROM problems")
    problems = c.fetchall()
    for x in range(len(users)):
        for y in range(len(problems)):
            print (x,users[x][0],y,problems[y][0],0,0)
            c.execute("INSERT INTO scoreboard VALUES (?,?,?,?,?,?)",(x,users[x][0],y,problems[y][0],0,0))
            conn.commit()

    
def fetch_problem(pid):
    c.execute("SELECT * FROM problems WHERE id='%s'"%(pid))    
    data = c.fetchall()[0]
    pdict = {}
    for x in range(len(pcols)):
        pdict[pcols[x]] = data[x]
    return pdict

def fetch_all_problems():
    c.execute("SELECT id, name FROM problems")
    data = c.fetchall()
    problems = []
    for col in data:
        problems.append({'id':col[0], 'name':col[1]})
    return problems
    

def fetch_valid_users():
    c.execute("SELECT name, password FROM users")
    data = c.fetchall()
    users = {}
    for col in data:
        users[col[0]] = {'pw':col[1]}
    return users

# create_scoreboard()    
