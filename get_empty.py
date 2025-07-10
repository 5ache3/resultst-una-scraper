import os
import json
lis=os.listdir('files')


lis2=[]
for file_n in lis:
    with open(f'files/{file_n}','r',encoding='utf-8') as f:
        file=json.load(f)
    
    if not file:
        lis2.append(file_n.replace('.json',''))

print(lis2)