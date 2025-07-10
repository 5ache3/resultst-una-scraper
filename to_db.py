import json
import mysql.connector
import hashlib

from get_list import *

db=mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    passwd="",
    database="FST2025"
)
pool=db.cursor()


def push_to_db(mat,fil):
    with open(f"files/{mat}.json","r",encoding="utf-8") as f :
        file=json.load(f)
    filliere=file['filiere']
    sem=file['semestre']
    moyenne=file['moyenne']
    decision=file['decision']
    semquery=f"""INSERT INTO SEMESTRES  (semestre,matricule,filliere,moyenne,decision,fil)
                    VALUES("{sem}","{mat}","{filliere}","{moyenne}","{decision}","{fil}");"""
    pool.execute(semquery)
    db.commit()
    for i in range(len(file['modules'])):
        module=file['modules'][i]
        module_name=module['name']
        decision_module=module['decision']
        moyenne_module=module['moyenne']
        modquery=f"""INSERT INTO MODULES(module,filliere,semestre,matricule,moyenne,decision,fil)
                        VALUES("{module_name}","{filliere}","{sem}","{mat}",{moyenne_module},"{decision_module}","{fil}");"""
        pool.execute(modquery)
        db.commit()
        for j in range(len(module['matiers'])):
            matier=file['modules'][i]['matiers'][j]
            name=matier['name']
            hash=hashlib.md5(f'{sem}{name}'.encode()).hexdigest()
            id=hash[:15]
            matquery=f"""INSERT INTO MATIERES(name,filliere,cof,note_tp,note_dev,note_exam,note_rat,note_finale,decision,module,matricule,semestre,fil,id)
                            VALUES("{matier['name']}","{filliere}",{matier['credit']},{matier['note_tp']},{matier['note_devoir']},{matier['note_examen']},{matier['note_ratrapage']},{matier['note_finale']},"{matier['decision']}","{module['name']}","{mat}","{sem}","{fil}","{id}");           """
            pool.execute(matquery)
            db.commit() 

lists=['L3-DAII','L2-DAII','L3-MIAGE','L2-MIAGE',]

for lis_name in lists:
    lis=get_list(lis_name)
    for item in lis:
        try:
            push_to_db(item,lis_name)
        except Exception as e:
            print(f'{item} error {e} ')
