# 1 - Definir pacotes
# 2 - Definir sintaxes
# 3 - Minerar todos os repositorios com python (1000)
# 4 - Buscar sintaxes dentro dos repositorios
import json
import requests
import time

from auth import token

# Editar username para o seu usuario
# Criar um arquivo auth.py no diretorio do script, com uma constante token = '(token gerado no github)'


# Definindo Sintaxes

# TensorFlow, Theano, Scikit-learn, Caffe, H2O, Amazon Machine Learning, Torch, Google Cloud ML Engine,
# Azure ML Studio, Spark ML lib, PyTorch

# Formas comuns de import em python: 

# from package import resource
# import package
# import package as name

frameworks = ['tensorflow', 'matplotlib', 'torch', 'pandas']
MLrepo = {}
MLrepo['total'] = 0
MLrepo['list'] = []

for package in frameworks:
        for x in range(1, 11):
                
                username = ''

                session = requests.Session()
                session.auth = (username,token)

                raw_data = []
                response = session.get("https://api.github.com/search/repositories?q=language:python&sort=stars&order=desc&per_page=100&page=" + str(x))
                raw_data.append(response.json())

                data = {}
                data['repository'] = []
                print(raw_data)
                for i in raw_data:
                        for j in i['items']:
                                data['repository'].append({'name': j['name'], 'link': j['html_url'], 'repo': j['full_name']})
                print("Data size:" + str(len(data['repository'])))

                limit = 0
                limit_1 = 0
                print("Wait 60 seconds")
                time.sleep(60)
                pause = 0
                
                for i in data['repository']:

                        #print("ToVerify1:")
                        #print(toVerify1)
                        #print("toVerify2:")
                        #print(toVerify2)
                        #print("ToVerify3:")
                        #print(toVerify3)
                        while True:
                                try:
                                        session = requests.Session()
                                        session.auth = (username,token)

                                        print(i['repo'])
                                        limit += 3
                                        limit_1 += 3
                                        status = session.get("https://api.github.com/rate_limit")
                                        status = status.json()
                                        print("Status:" + str(status['resources']['search']))
                                        print(status)
                                        if limit == 24:
                                                print("Wait 60seconds")
                                                time.sleep(60)
                                                limit = 0    
                                        if pause == 10:
                                                print("System pause.")
                                                print("-------------------------------------------------")
                                                time.sleep(60)
                                                pause = 0
                                        string1 = "\"from "+str(package)+" import\""                
                                        string2 = "\"import "+str(package)+"\""
                                        string3 = "\"import "+str(package)+" as\""
                                        toVerify1 = session.get("https://api.github.com/search/code?q="+str(string1)+"in:file+language:python+repo:"+str(i['repo'])) 
                                        time.sleep(1)              
                                        toVerify2 = session.get("https://api.github.com/search/code?q="+str(string2)+"in:file+language:python+repo:"+str(i['repo']))    
                                        time.sleep(1)           
                                        toVerify3 = session.get("https://api.github.com/search/code?q="+str(string3)+"in:file+language:python+repo:"+str(i['repo']))               
                                        time.sleep(1)

                                        toVerify1 = toVerify1.json()
                                        toVerify2 = toVerify2.json()
                                        toVerify3 = toVerify3.json()

                                        if toVerify1['total_count'] > 0:
                                                MLrepo['list'].append({'package': str(package), 'result_1': toVerify1})
                                                MLrepo['total'] += 1
                                        if toVerify2['total_count'] > 0:
                                                MLrepo['list'].append({'package': str(package), 'result_2': toVerify2})
                                                MLrepo['total'] += 1                      
                                        if toVerify3['total_count'] > 0:
                                                MLrepo['list'].append({'package': str(package), 'result_3': toVerify3})
                                                MLrepo['total'] += 1

                                        break
                                except:
                                        print("EXCEPTION -----------------------------------------------------")
                                        print("ToVerify1:")
                                        print(toVerify1)
                                        print("toVerify2:")
                                        print(toVerify2)
                                        print("ToVerify3:")
                                        print(toVerify3)
                                        print("WAIT 10 MINUTES -----------------------------------------------")
                                        time.sleep(600)
                print("Page" + str(x))
                print("--------------------------------------------------------------")
                time.sleep(60)

        for i in MLrepo['list']:
                print(i)
                
        with open(str(package) + '_data.json', 'w') as f:
                json.dump(MLrepo, f,sort_keys=True, indent=4)
