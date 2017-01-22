import sqlite3
import operator
from datetime import datetime,timedelta

conn = sqlite3.connect('codechecker.db', check_same_thread=False)
c = conn.cursor()

pcols = ['id', 'name', 'descr', 'tlimit', 'input', 'output']



def fetch_scoreboard():
    # get contest clock time
    with open("contest_clock.txt", 'r') as f:
        ctime = datetime.strptime(f.read() ,"%Y-%m-%d %H:%M:%S.%f")
    
    c.execute("SELECT name FROM users")
    users = [x[0] for x in c.fetchall()]

    rows = []
    for user in users:
        c.execute("SELECT * FROM scoreboard WHERE uname = ?",(user,))
        status = zip(*c.fetchall())

        # username
        username = user
        # net score
        score = sum(status[4])
        # wrong subs
        WAs = sum(status[6])
        # net time 
        intervals = [ctime - datetime.strptime(t ,"%Y-%m-%d %H:%M:%S.%f") for t in status[5] if t != None]
        net_time = sum(intervals,timedelta()) + timedelta(minutes=5*WAs)
        # solved problems
        row = [username, score, net_time]
        row.extend(status[4])
        rows.append(row)
        
        
    # sort rows on basis of 1.score  2.total time 
    rows.sort(key = operator.itemgetter(1,2), reverse = True)

    rows = [[(i+1)] + rows[i][:2] + rows[i][3:] for i in range(len(rows))]
    return rows
   
#fetch_scoreboard()    


def update_score(username, pid, result):
    if result == "Fail":
        c.execute("UPDATE scoreboard SET wrong_sub = wrong_sub+1 WHERE uname = ? AND pid = ?", (username, pid))
    else:
        time = datetime.now()
        c.execute("UPDATE scoreboard SET status = 1, time = ? WHERE uname = ? AND pid = ? AND status = 0", (str(time), username, pid))
    conn.commit()
   

def initialize_scoreboard():
    # delete old scoreboard
    c.execute("DELETE FROM scoreboard")

    c.execute("SELECT name FROM users")
    users = c.fetchall()

    c.execute("SELECT name FROM problems")
    problems = c.fetchall()
    for x in range(len(users)):
        for y in range(len(problems)):
            c.execute("INSERT INTO scoreboard VALUES (?,?,?,?,?,?,?)",(x+1,users[x][0],y+1,problems[y][0],0,None,0))
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
