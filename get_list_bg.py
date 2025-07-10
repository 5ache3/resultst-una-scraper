from get_list import *
import json

file=get_unregistred_list('L1-BG')

with open('list_bg.json','w',encoding='utf-8') as f:
    json.dump(file,f,indent=2)
