# importing the requests library 
import requests 

# api-endpoint 
URL = "http://172.16.2.12:8088/ws/v1/cluster/apps?state=FINISHED"

# sending get request and saving the response as response object 
r = requests.get(url = URL) 

# extracting data in json format 
data = r.json()

# sum all the 'elapsedTime' field values
cpu_time = 0
number_of_iteration = 0

# result computation
length = len(data['apps']['app'])
for i in range(0, length):
    #print(i)
    cpu_time += data['apps']['app'][i]['elapsedTime']
    number_of_iteration += 1

# print results
print('Number of Iterations: ' + str(number_of_iteration))
print(cpu_time)
 