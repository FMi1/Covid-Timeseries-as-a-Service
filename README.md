# Cloud Computing Project
Cloud Computing OpenStack project developed on a cluster of VMs hosted on University servers. The project specification can be found in [..]
## OpenStack Project: Timeseries-as-a-Service
We decided to build a simple GUI in order to show the Italy Covid-related data (both for each single Region and the sum aggregate for Italy-related data) provided by Protezione Civile until a certain day; subsequent data have been randomly produced.

The application consists in a container which runs a Flask server, this component is responsible to build a simple REST API in order manage HTTP requests issued by a producer. These requests are handled through an interaction with a Gnocchi DB hosted in another container.

Both the Producer and the Consumer have been created through the OpenStack Horizon Dashboard and  have been inserted in the admin domain so that they have privileges that allow them to retrieve the list of the metrics stored in Gnocchi.

The Consumer is mainly responsible to create a REST application using Flask (the main function only runs the Flask server). The flask server contains an handlers collection in order to manage all the HTTP Requests issued by the producer to given endpoints (each handler starts with @app.route('endpoint)).
Two fundamental statements used inside the code are the following:
- `redirect(url_for(endpoint))`: issues an HTTP request to a given endpoint
- `render_template(pagina.html)`: updates the GUI, the HTML code is located inside the directory [..]


Since the project was meant to test the understanding of the OpenStack mechanisms acquired during the cloud computing course, all the IP address used inside the files are static so it is difficult to provide the way to launch the program. For a better understanding of the functioning we try to provide some information inside this README.md file and inside the code using comments.

## Gnocchi
[Gnocchi](https://gnocchi.xyz/) stores metrics and resources and provides a REST API in order to manipulate them. In this project we stored only metrics: each Region is a metric, this is created inside the Gnocchi DB and stored on Ceph according to a certain archive-policy. Gnocchi does not store each single datum but instead stores aggregates: an archive-policy defines the lifespan, the granularity and the aggregate type to be stored for a certain metric.

In this case we defined a new archive-policy called _years_rate_ with _timespan_ equal to one year, _granularity_ equal to one day and sum as _aggregate type_.

The Gnocchi container has been built through the command (please pay attention to the final dot in order to specify the current directory)
```
docker build -t docker_gnocchi .
```

## Dockerfile
- `FROM`: specifies the image from the central repository to be used, _Alpine_ is a Python lightweigth version
- `RUN`: specifies the command to be executed inside the container at installation time (in this case we need to create a directory in which we insert the _requirements.txt_ file containing the requirements to be installed through `pip3`)
-	`EXPOSE`: in order to publicly expose a service running inside a container to external networks we need to perform 2 steps: 
  sub 1. configure a container in order to expose a service through a certain UDP/TCP port. In this case in order to receive http requests we need to expose the service on port 8080;
  sub 2.  map the chosen port in one of the public ports of the public IP address of the system which is hosting the server. For this reason the container is launched with the command: 
```docker run -p 5000:8080 -it server-consumer```
This command tells the container to execute the docker image and to open a shell inside the container once the program will be executed.
-	`ENTRYPOINT, CMD`: these fields allow to specify the command to be executed when the container is started and could have been done also through the command
`CMD ["/usr/bin/python3", "/root/my_program.py"]`
  
In order to stop a container:
- `docker ps`: in order to get the running container list
- `docker stop <ID>`: in order to stop one of the running container to be stopped


Markup : * Bullet list
              * Nested bullet
                  * Sub-nested bullet etc
          * Bullet list item 2
