
import json 
from bs4 import BeautifulSoup
import hashlib
import time
from playwright.sync_api import sync_playwright
from get_list import *
import mysql.connector
db=mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    passwd="",
    database="FST2025"
)
pool=db.cursor()

def push_to_db(file,mat,fil):
    filliere=file['filiere']
    sem=file['semestre']
    moyenne=file['moyenne']
    decision=file['decision']
    amphi=''
    try:
        amphi=file['sub_filiere'][0]
    except:
        pass
    semquery=f''' INSERT INTO SEMESTRES  (semestre,matricule,filliere,moyenne,decision,fil,amphi)
                    VALUES("{sem}","{mat}","{filliere}","{moyenne}","{decision}","{fil}","{amphi}");'''
    pool.execute(semquery)
    db.commit()
    for i in range(len(file['modules'])):
        module=file['modules'][i]
        module_name=module['name']
        decision_module=module['decision']
        moyenne_module=module['moyenne']
        modquery=f''' INSERT INTO MODULES(module,filliere,semestre,matricule,moyenne,decision,fil,amphi)
                        VALUES("{module_name}","{filliere}","{sem}","{mat}",{moyenne_module},"{decision_module}","{fil}","{amphi}");'''
        pool.execute(modquery)
        db.commit()
        for j in range(len(module['matiers'])):
            matier=file['modules'][i]['matiers'][j]
            name=matier['name']
            hash=hashlib.md5(f'{sem}{name}'.encode()).hexdigest()
            id=hash[:15]
            matquery=f''' INSERT INTO MATIERES(name,filliere,cof,note_tp,note_dev,note_exam,note_rat,note_finale,decision,module,matricule,semestre,fil,id,amphi)
                            VALUES("{matier['name']}","{filliere}",{matier['credit']},{matier['note_tp']},{matier['note_devoir']},{matier['note_examen']},{matier['note_ratrapage']},{matier['note_finale']},"{matier['decision']}","{module['name']}","{mat}","{sem}","{fil}","{id}","{amphi}");           '''
            pool.execute(matquery)
            db.commit() 

def update_db(file,mat,fil):
    filliere=file['filiere']
    sem=file['semestre']
    moyenne=file['moyenne']
    decision=file['decision']
    modules=file['modules']
    amphi=''
    try:
        amphi=file['sub_filiere'][0]
    except:
        pass
    pool.execute(f"DELETE FROM semestres WHERE matricule='{mat}' AND semestre='{sem}'")
    semquery=f''' INSERT INTO SEMESTRES  (semestre,matricule,filliere,moyenne,decision,fil,amphi)
                    VALUES("{sem}","{mat}","{filliere}","{moyenne}","{decision}","{fil}","{amphi}");'''
    
    pool.execute(semquery)
    db.commit()
    for i in range(len(modules)):
        module=modules[i]
        module_name=module['name']
        decision_module=module['decision']
        moyenne_module=module['moyenne']
        pool.execute(f"DELETE FROM modules WHERE matricule='{mat}' AND module='{module_name}'")
        modquery=f''' INSERT INTO MODULES(module,filliere,semestre,matricule,moyenne,decision,fil,amphi)
                        VALUES("{module_name}","{filliere}","{sem}","{mat}",{moyenne_module},"{decision_module}","{fil}","{amphi}");'''
        pool.execute(modquery)
        db.commit()
        for j in range(len(module['matiers'])):
            matier=file['modules'][i]['matiers'][j]
            name=matier['name']
            hash=hashlib.md5(f'{sem}{name}'.encode()).hexdigest()
            id=hash[:15]
            pool.execute(f"DELETE FROM matieres WHERE matricule='{mat}' AND id='{id}'")

            matquery=f''' INSERT INTO MATIERES(name,filliere,cof,note_tp,note_dev,note_exam,note_rat,note_finale,decision,module,matricule,semestre,fil,id,amphi)
                            VALUES("{matier['name']}","{filliere}",{matier['credit']},{matier['note_tp']},{matier['note_devoir']},{matier['note_examen']},{matier['note_ratrapage']},{matier['note_finale']},"{matier['decision']}","{module['name']}","{mat}","{sem}","{fil}","{id}","{amphi}");           '''
            pool.execute(matquery)
            db.commit() 

def getInfos(soup):
    sub_filliere=''
    sub_profil=''
    filliere=''
    profil=''
    spans=soup.find_all('span')
    for i in range(len(spans)):
        spans[i]=spans[i].text
    for i in range(len(spans)):
        if spans[i].replace(' ','')=='Nom/Prénom':
            nom=spans[i+1]
        if spans[i]=='Profil':
            filliere=spans[i+1]
            sub_filliere=spans[i+2]

        if spans[i]=="Profil d'orientation : " :
            profil=spans[i+1]
            sub_profil=spans[i+2]

    return {"nom":nom,"fil":profil,"sub_fil":sub_profil,"class":filliere,"sub_class":sub_filliere}

def getSemDetails(soup):
    sub_tables=soup.find_all('table')
    moyenne=sub_tables[0].find_all('span')[1].text
    decision=sub_tables[2].find_all('span')[1].text
    return {"moyenne":moyenne,"decision":decision}

def getMatiere(table,i,t_id,t_col_id):
    matieres=[]
    'ecriture:j_id207:0:j_id234:0:j_id235'
    m_ind=235
    for j in range(len(table)):

        matiere_name=table.find('td',id=f'{t_id}:{i}:{t_col_id}:{j}:j_id{m_ind+2*0}').find('span').text
        credit      =table.find('td',id=f'{t_id}:{i}:{t_col_id}:{j}:j_id{m_ind+2*1}').find('span').text.replace(',','.')
        Note_tp     =table.find('td',id=f'{t_id}:{i}:{t_col_id}:{j}:j_id{m_ind+2*2}').find('span').text.replace(',','.')
        Note_dev    =table.find('td',id=f'{t_id}:{i}:{t_col_id}:{j}:j_id{m_ind+2*3}').find('span').text.replace(',','.')
        Note_exam   =table.find('td',id=f'{t_id}:{i}:{t_col_id}:{j}:j_id{m_ind+2*4}').find('span').text.replace(',','.')
        Note_rat    =table.find('td',id=f'{t_id}:{i}:{t_col_id}:{j}:j_id{m_ind+2*5}').find('span').text.replace(',','.')
        Note_final  =table.find('td',id=f'{t_id}:{i}:{t_col_id}:{j}:j_id{m_ind+2*6}').find('span').text.replace(',','.')
        decision    =table.find('td',id=f'{t_id}:{i}:{t_col_id}:{j}:j_id{m_ind+2*7}').find('span').text.replace(',','.')
        matiere_file={
            "name":matiere_name,
            "credit":int(float(credit.strip())),
            "note_tp":float(Note_tp.strip()),
            "note_devoir":float(Note_dev.strip()),
            "note_examen":float(Note_exam.strip()),
            "note_ratrapage":float(Note_rat.strip()),
            "note_finale":float(Note_final.strip()),
            "decision":decision
        }

        matieres.append(matiere_file)
    return matieres

def getModules(soup):
    t_id='ecriture:j_id207'
    t_col_id='j_id234'
    t_ind=252
    table=soup.find('tbody',id=f"{t_id}:tb")
    modules=[]
    for i in range(len(table)):
        module_name    =soup.find('td',id=f'{t_id}:{i}:{t_col_id}:j_id{t_ind+13*0}').find_all('span')[1].text
        moyenne_module =soup.find('td',id=f'{t_id}:{i}:{t_col_id}:j_id{t_ind+13*1}').find('span').text
        decision_module=soup.find('td',id=f'{t_id}:{i}:{t_col_id}:j_id{t_ind+13*2-10}').find('span').text
        module_file={
            "name":f"{module_name}",
            "moyenne": float(moyenne_module.replace(',','.')),
            "decision": decision_module,
            "matiers":[]
            }
        module_file['matiers']=getMatiere(soup.find('tbody',id=f'{t_id}:{i}:{t_col_id}:tb'),i,t_id=t_id,t_col_id=t_col_id)
        modules.append(module_file)
    return modules

def getPerson(matricule,semestre):
    try :
        with sync_playwright() as p:

            browser=p.chromium.launch()
            page=browser.new_page()
            page.set_default_timeout(60000)
            page.goto('http://193.146.150.198/FST/') 
            page.fill('input.rsinputTetx',f'{matricule}\n')
            button = page.query_selector('input.rsinputTetx')
            button.press('Enter')
            page.wait_for_load_state("networkidle")
            soup=BeautifulSoup(page.inner_html('body'),'lxml')
            option=soup.find('option',value=semestre)
            if not option:
                print("semestre not found")
                with open('semestre_not_found.txt','a',encoding='utf-8') as f:
                    f.write(f'{matricule}\n')
                return
            
            
            
            infos=getInfos(soup)
            dropdown = page.wait_for_selector('select.rsinputTetx')
            dropdown.select_option(semestre)

            time.sleep(4)
            page.wait_for_load_state("networkidle")
            soup=BeautifulSoup(page.inner_html('body'),'lxml')
            nom=infos['nom']
            filiere=infos['fil']
            if infos['fil']=='' : filiere=infos['class']
            sub_filiere=infos['sub_fil']
            if infos['sub_fil']=='' : sub_filiere=infos['sub_class']

            footer_table=soup.find('td',id='ecriture:j_id207:j_id271')
            res=getSemDetails(footer_table)
            moyenne=float(res['moyenne'].replace(',','.'))
            decision=res['decision']
            file={"matricule":matricule,"nom":nom,"filiere":filiere,"semestre":semestre,"moyenne":moyenne,"decision":decision}

            modules=getModules(soup)
            
            file['modules']=modules

            return file
            
    except Exception as e :
        print("error",e) 
        with open("erors.txt","a",encoding="utf-8") as f :
            f.write(f'{matricule}\n')   
        return

def get_list_from_file(file_path):
    try:
        with open(file_path,"r",encoding="utf-8") as f :
            file=json.load(f)
        return file
    except:
        return []

def get_not_found(file_path):
    try:
        with open(file_path,"r",encoding="utf-8") as f :
            text_f=f.read()
        return text_f.split('\n')
    except:
        return []

def save_to_File(file,path):
    with open(f'{path}.json','w',encoding='utf-8') as f:
        json.dump(file,f,indent=2)

filliere=get_registred_fils()
filliere=['L2-DAII']

for fil in filliere:
    try:
        if 'L1' in fil:
            sem='S2'
        elif 'L2' in fil:
            sem='S4'
        else:
            sem='S6'

        lis=get_list(fil)
        lis=get_unregistred_list(fil,sem)
        lis.reverse()
        i=0
        l=len(lis)
        for mat in lis:
            i+=1
            print(f'{fil} {mat} {i}/{l}')
            file=getPerson(mat,sem)
            if file :
                update_db(file,mat,fil)
                save_to_File(file,f'new/{mat}')
    except Exception as e:
        print(fil,e)
        
