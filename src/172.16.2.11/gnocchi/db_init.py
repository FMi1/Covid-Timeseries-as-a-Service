import json
from keystoneauth1.identity import v3
import requests
from keystoneauth1 import session
import datetime
from datetime import timedelta

"""
The first thing to be done is the Keystone authentication through the keystoneclient API, 
this way it will open a session through which it will require a token to authenticate all the 
requests of interactions with Gnocchi metrics. In particular, the session object will provide an
authentication plugin, SSL/TLS certificates and other data related to security.
The token will be inserted in each HTTP request header through the REST API in the X-AUTH-TOKEN field.
"""
auth = v3.Password(auth_url='http://252.3.54.190:5000/v3',
                   username='Producer',
                   password='producer',
                   project_name='admin',
                   user_domain_id='73a5787f8eda435ca585fab958883e53',
                   project_domain_id='73a5787f8eda435ca585fab958883e53')
sess = session.Session(auth=auth)
token = sess.get_token()
session = requests.Session()
session.headers.update({'X-AUTH-TOKEN': token})

# -- Archive Policy creation--
archive_policy_data='{"aggregation_methods": ["sum"],"back_window":0,"definition":[{"granularity":"1 day","timespan":"365 day"}],"name":"year_rate"}'
response=session.post('http://252.3.54.57:8041/v1/archive_policy/',data=archive_policy_data,headers={'Content-Type':'application/json'})

# -- Metrics creation --
"""
Array of strings definition, this will be used in the following loop in order to creare a metric
for each Region which will be stored with the year-rate archive-policy through an HTTP POST Request
to the metrics endpoint.
""" 

regionsname = [
    ["abruzzo","Abruzzo"],
    ["basilicata","Basilicata"],
    ["calabria","Calabria"],
    ["campania","Campania"],
    ["emiliaromagna", "Emilia-Romagna"],
    ["friuliveneziagiulia","Friuli Venezia Giulia"],
    ["lazio","Lazio"],
    ["liguria","Liguria"],
    ["lombardia","Lombardia"],
    ["marche","Marche"],
    ["molise","Molise"],	
    ["piemonte","Piemonte"],	
    ["puglia","Puglia"],	
    ["sardegna","Sardegna"],	
    ["sicilia","Sicilia"],
    ["toscana","Toscana"],
    ["trentinoaltoadige","P.A. Trento"],
    ["umbria","Umbria"],	
    ["valledaosta","Valle d'Aosta"],
    ["veneto","Veneto"]
]

for region in regionsname:
    mydata='{ "archive_policy_name": "year_rate", "name":"'+region[0]+'" }'
    response=session.post('http://252.3.54.57:8041/v1/metric/',data=mydata,headers={'Content-Type':'application/json'})

# -- obtaining IDs --
"""
In order to insert the Protezione Civile data stored in the data.json file we need first to issue
an HTTP GET request, the HTTP response will be JSON parsed in order to extract the metrics IDs to
create the metrics ID list.
"""

response = session.get('http://252.3.54.57:8041/v1/metric/')
metrics_list=json.loads(response.text)
for metric in metrics_list:
    for region in regionsname:
        if region[0]==metric['name']:
            region.append(metric['id']) 


# -- Insert measures through metrics --
"""
Issuing of HTTP POST Requests to store data inside Gnocchi:
region[1] is the name of the Region (the first letter is in uppercase)
region[2] is the extracted ID
"""

with open('data.json') as json_file: 
    dataj = json.load(json_file)

for region in regionsname:    
    for item in dataj:
        if item['denominazione_regione'] == region[1]:
            b=datetime.datetime.strptime(item['data'],'%Y-%m-%dT%H:%M:%S')
            mydata='[{"timestamp":"'+item['data']+'", "value":'+str(item['nuovi_positivi'])+'}]'
            response=session.post('http://252.3.54.57:8041/v1/metric/'+region[2]+'/measures', data=mydata, headers={'Content-Type':'application/json'})
            print(mydata)