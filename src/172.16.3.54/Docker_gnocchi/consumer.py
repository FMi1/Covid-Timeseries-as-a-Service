from flask import Flask,render_template,request,redirect,url_for
from keystoneauth1.identity import v3
from keystoneauth1 import exceptions as ks_exception
import requests
from keystoneauth1 import session
import json
import datetime
from string import Template


#global variable in order to signal if the authentication is successfull or not
Authorized=False

sessionRequest = requests.Session()
app = Flask(__name__)


"""
Handler responsible of the GUI creation through the login.html file: this file
contains a form whose related action makes an HTTP POST request to the "/login" endpoint
"""
@app.route('/')
def index():
    if Authorized == True:
        return render_template('front_end.html')
    return render_template('login.html')

"""
Handler to perform the OpenStack Keystone authentication.
It basically extracts the list of the parameters written in the form and it uses them to
perform the token-based Keystone authentication: so initially we need to request for
a token which will be inserted in the HTTP Request header that will be issued during the
established session.
At the end of the handler an HTTP Request to the endpoint "/covidapi" is issued
"""
@app.route('/login', methods = ['POST'])
def user():
    global Authorized,sessionRequest
    data = request.form # a multidict containing POST data
    auth = v3.Password(auth_url='http://252.3.54.190:5000/v3',
                username=data.get('name'),
                password=data.get('Password'),
                project_name='admin',
                user_domain_id='73a5787f8eda435ca585fab958883e53',
                project_domain_id='73a5787f8eda435ca585fab958883e53')
    sess = session.Session(auth=auth)
    try:
        token=sess.get_token()
        sessionRequest.headers.update({'X-AUTH-TOKEN': token})
    except ks_exception.Unauthorized:
        print("Domain admin client authentication failed")
        return redirect(url_for('index'))
    Authorized=True
    return redirect(url_for('covidapi'))


"""
The global variable Authenticate determines if the Keystone authentication is successful or not.
This handler simply redirects the user:
- to the index.html page if the authentication fails (Authenticate = False)
- to the font_end.html page in case of successful (Authenticate = True)
"""
@app.route('/covidapi')
def covidapi():
    if Authorized == True:
        return render_template('front_end.html')
    return render_template('login.html')
 

"""
The handler issues a GET request to the Gnocchi container IP address, then it parses the response payload
to JSON and extracts from it the name of all the metrics (in this case of all the Regions) to build
an array used for the rendering of the regions.html page.
The latter exploits the metrics name vector in order to dinamically build <div>, each one of them 
allows to make a request to the endpoint "/regions/<metric_name>"
"""
@app.route('/regions')
def regions():
    if Authorized == True:
        response = sessionRequest.get('http://252.3.54.57:8041/v1/metric/')
        dataj=json.loads(response.text)
        metrics=[]
        for item in dataj:
            metrics.append(item['name'])
        return render_template('regions.html',metrics=metrics)
    return render_template('login.html')

"""
The handler issues the same GET request to the Gnocchi container IP address in order to retrieve all
the metrics, the it issues a second HTTPRequest in order to query for the sum aggregate related to
the requested metric threough the ID extracted from the parsed payload of the HTTP Response returned
by the previous request
"""
@app.route('/regions/<region>')
def api_regions(region):
    if Authorized == True:
        response = sessionRequest.get('http://252.3.54.57:8041/v1/metric/')
        metrics_list=json.loads(response.text)
        for item in metrics_list:
            if item['name'] == region:
                response = sessionRequest.get('http://252.3.54.57:8041/v1/metric/'+item['id']+'/measures?aggregation=sum')
                items=json.loads(response.text)
                x_values = [ item[0] for item in items] 
                y_values = [ item[2] for item in items]
                y2_values = []
                y2_values.append(items[0][2])
                for item in items:
                    new=y2_values[-1]
                    y2_values.append(item[2]+new)
                data = {"timestamps": x_values, "values": y_values,"total_positives":y2_values}  
        return render_template('graph.html',data=data)
    return render_template('login.html')


"""
First of all the handler performs the request to the Gnocchi endpoint in order to retrieve the list of
all the metrics. Using templates we start to issue HTTP request in order to retrieve all the sum aggregates
related to all the Regions (to all the metrics). Once the payload is JSON parsed we use only the
"measures" and the "aggregated" fields in order to obtain the data useful to build the graph for Italy
in the same way we did for the Regions.
"""
@app.route('/italy')
def italy():
    if Authorized == True:
        italy = Template('{"operations":"(aggregate sum (metric $all_metrics))"}')
        mydata=''
        response = sessionRequest.get('http://252.3.54.57:8041/v1/metric/')
        dataj=json.loads(response.text)
        for item in dataj:
            mydata=mydata+'('+item['id']+' sum)'
        mydata=italy.substitute(all_metrics=mydata)
        response = sessionRequest.post('http://252.3.54.57:8041/v1/aggregates/',data=mydata, headers={'Content-Type':'application/json'})
        items=json.loads(response.text)
        items=items['measures']['aggregated']
        x_values = [ item[0] for item in items] 
        y_values = [ item[2] for item in items]
        y2_values = []
        y2_values.append(items[0][2])
        for item in items:
            new=y2_values[-1]
            y2_values.append(item[2]+new)
        data = {"timestamps": x_values, "values": y_values,"total_positives":y2_values} 
        return render_template('graph.html',data=data)
    return render_template('login.html')




if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080)
