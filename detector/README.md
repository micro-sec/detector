# Detector

This folder contains the CLI, Web Dashboard, the API Server and the intrusion detection. The connection to the Local Storage is also established here. The algorithms folder has the implementation of the algorithms (bosc and STIDE). The static folder has static files such as scripts, CSS files, images, etc... that must be sent to the browser when requested. The templates folder has the html (JINJA templates) necessary to present the dashboard to the user. The file main.py is the entrypoint for the Flask app. Some settings can be found in the config.py file and the classes.py contains structures used to agents and configs. The cli.py allows the user to interact with the tool via a command-line interface and the dashboard.py is a blueprint for the web dashboard. The api.py file corresponds to the API Server (and its endpoints) in the tool's architecture. All the other utility functions can be found in the utils.py file.



### µDetector API
| Method | URL              | Description                                                                                                                                 |
|---------------|----------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| GET           | /api                       | Returns the string "The detector API"                                                                                                      |
| GET           | /api/daemon/status         | Establishes a connection to the Daemon and returns status code 200                                                                          |
| GET           | /api/daemon/agents         | Establishes a connection to the Daemon and returns a json with information about the nodes and whether they are running agents or not |
| POST          | /api/monitoring/start      | Establishes a connection to the Agent and sends a request to start collecting system calls                                                  |
| POST          | /api/monitoring/stop       | Establishes a connection to the Agent and sends a request to stop collecting system calls                                                   |
| POST          | /api/inspecting/start      | Starts an intrusion detection instance                                                                                                      |
| POST          | /api/inspecting/stop       | Stops all intrusion detection instances or a single one if an id is provided                                                                |
| GET           | /api/alarms                | Returns a list of all the alarms sorted by most recent. It is also possible to retrieve the latest N alarms                             |
| DELETE        | /api/alarms                | Deletes the list of alarms                                                                                                                  |
| GET           | /api/algorithms            | Returns a list of the algorithms available                                                                                                  |
| GET           | /api/resources/pods        | Returns information about the pods of the Kubernetes cluster                                                                                |
| GET           | /api/resources/services    | Returns information about the services of the Kubernetes cluster                                                                            |
| GET           | /api/resources/deployments | Returns information about the deployments of the Kubernetes cluster                                                                         |
| GET           | /api/resources/namespaces  | Returns information about the namespaces of the Kubernetes cluster                                                                          |
| GET           | /api/nodes                 | Returns information about the nodes of the Kubernetes cluster                                                                               |
| GET           | /api/stats                 | Returns a list of all the statistics from the monitoring phase                                                                              |
