
import mysql.connector

db=mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    passwd="",
    database="FST2025"
)
pool=db.cursor()

def get_list(fil):
    lis=[]
    pool.execute(f"""SELECT matricule from etudiants where fil="{fil}" """)
    # pool.execute('select distinct fil from etudiants')

    for item in pool:
        lis.append(item[0])
    return lis

def get_unregistred_list(fil,sem):
    lis=[]
    pool.execute(f"""SELECT matricule from etudiants where fil='{fil}' AND matricule not in (select matricule from semestres WHERE semestre = '{sem}') """)
    # pool.execute('select distinct fil from etudiants')

    for item in pool:
        lis.append(item[0])
    return lis

def get_registred_fils():
    lis=[]
    pool.execute(f"""SELECT DISTINCT fil FROM semestres """)
    # pool.execute('select distinct fil from etudiants')

    for item in pool:
        lis.append(item[0])
    return lis
