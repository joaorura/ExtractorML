#1 - Definir pacotes
#2 - Definir sintaxes
#3 - Minerar todos os repositorios com python (1000) 
#4 - Buscar sintaxes dentro dos repositorios
import json, requests
from auth import token
import time

#Editar username para o seu usuário
#Criar um arquivo auth.py no diretório do script, com uma constante token = '(token gerado no github)'

username = ''

session = requests.Session()
session.auth = (username,token)


# Definindo pacotes

raw_data = []
for i in range(0,5):
        raw_data.append(0)        
for i in range(0,5):
        response = session.get("https://api.github.com/search/repositories?q=language:python&sort=stars&order=desc&per_page=100&page=" + str(i+1))
        raw_data[i] = response.json()

data = {}
data['repository'] = []
for i in raw_data:
        for j in i['items']:
                data['repository'].append({'name': j['name'], 'link': j['html_url'], 'repo': j['full_name']})

# Definindo Sintaxes

# TensorFlow, Theano, Scikit-learn, Caffe, H2O, Amazon Machine Learning, Torch, Google Cloud ML Engine,
# Azure ML Studio, Spark ML lib, PyTorch

# Formas comuns de import em python: 

# from package import resource
# import package
# import package as name

frameworks = ['tensorflow']
MLrepo = {}
MLrepo['list'] = []
time.sleep(60)
count = 0
aux = 0
for package in frameworks:
        for i in data['repository']:
                count += 3
                aux += count
                print("Number of repositories checked: " + str(aux))
                if count == 24:
                        print("Wait 60seconds")
                        time.sleep(60)
                        count = 0           
                string1 = "\"from "+str(package)+" import\""                
                string2 = "\"import "+str(package)+"\""
                string3 = "\"import "+str(package)+" as\""
                toVerify1 = session.get("https://api.github.com/search/code?q="+str(string1)+"in:file+language:python+repo:"+str(i['repo']))               
                toVerify2 = session.get("https://api.github.com/search/code?q="+str(string2)+"in:file+language:python+repo:"+str(i['repo']))               
                toVerify3 = session.get("https://api.github.com/search/code?q="+str(string3)+"in:file+language:python+repo:"+str(i['repo']))               
                
                toVerify1 = toVerify1.json()
                toVerify2 = toVerify2.json()
                toVerify3 = toVerify3.json()
                        
                #print("ToVerify1:")
                #print(toVerify1)
                #print("toVerify2:")
                #print(toVerify2)
                #print("ToVerify3:")
                #print(toVerify3)
                        
                if toVerify1['total_count'] > 0:
                        MLrepo['list'].append({'package': str(package), 'result_1': toVerify1})
                if toVerify2['total_count'] > 0:
                        MLrepo['list'].append({'package': str(package), 'result_2': toVerify2})                      
                if toVerify3['total_count'] > 0:
                        MLrepo['list'].append({'package': str(package), 'result_3': toVerify3})
                        

for i in MLrepo:
        print(i)
