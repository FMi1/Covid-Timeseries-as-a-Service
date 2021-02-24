
from keystoneauth1.identity import v3
import requests
from keystoneauth1 import session
import json
import datetime
import random
from time import sleep
from string import Template

metrics_template=Template('{$all_metrics}')
metric_template=Template('"$id":[{"timestamp":"$timestamp","value":$value}],')

"""
Function to get the timestamp associated to the last datum using an HTTP GET Request: the 
HTTP Response is then parsed in JSON. The obtained timestamp is then incremented in order to
create a new one.
This action is fundamental since Gnocchi stores data in order to guarantee sequential consistency:
if you try to insert a data associated with a timestamp older then the most recent one it will
not be inserted and will be discarded (the back_window=0 in the archive policy does not allow
us to insert older data). 
"""
def get_last_timestamp():
    ts_response=session.get('http://252.3.54.57:8041/v1/metric/'+json_id[0]['id']+'/measures?aggregation=sum')
    actual_timestamp=json.loads(ts_response.text)[-1][0][:-6]
    new_timestamp=datetime.datetime.strptime(actual_timestamp, '%Y-%m-%dT%H:%M:%S')
    new_timestamp=new_timestamp+datetime.timedelta(1)
    return new_timestamp

"""
The first thing the producer must do is the Keystone authentication through the keystoneclient API, 
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

response=session.get('http://252.3.54.57:8041/v1/metric')
json_id=json.loads(response.text)

new_timestamp=get_last_timestamp()
print("starting from timestamp: " + str(new_timestamp))

"""
Infinite Loop which produced random artificial data in Gnocchi compliant format using the templates.
Each time we concatenate to my data a new random datum in the range 1-10 to be inserted in the DB.
At this point we simulate a data update through batching: we simulated a data transmission at 6-hours steps:
this is done issuing an HTTP Post request in which we request Gnocchi to store the measures created in
mydata, then we create the timestamp to be used in the next HTTP Post Request and we sleep for
a random time-interval (expressed in seconds), in order to not overload Gnocchi.
"""
while True:
    mydata=''
    for item in json_id:
        mydata=mydata+metric_template.substitute(id=item['id'],timestamp=new_timestamp.isoformat(),value=str(random.randint(1,10)))
    mydata=mydata[:-1]
    mydata=metrics_template.substitute(all_metrics=mydata)
    new_timestamp=new_timestamp+datetime.timedelta(0,60*360)
    response=session.post('http://252.3.54.57:8041/v1/batch/metrics/measures', data=mydata, headers={'Content-Type':'application/json'})
    print("sending metrics batch")
    sleep(random.randint(1,60))


