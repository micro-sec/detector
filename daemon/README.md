# Daemon

This component is deployed on a Master node of the Kubernetes cluster. It works as a proxy which allows the µDetector tool, running on an external machine, to communicate with the Kubernetes API to retrieve information about the cluster such as available pods and nodes. Additionally, when a user provides a specific monitoring configuration, the daemon is responsible for communicating with the monitoring agents in the worker nodes. It is written in Python using the Flask web framework.

### Daemon API
| Method | URL              | Description                                                                                                                                 |
|---------------|----------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| GET           | /status                       | This method always returns 200 and is used to verify that the connection to the daemon is working                                                                                                      |
| GET           | /agents         | This method is used to verify if the monitoring agents are running on the worker nodes. It returns a JSON with information about the nodes and whether they are running agents or not              |
| POST           | /start         | This method forwards a POST request to the monitoring agents on the worker nodes to start collecting system calls |
| POST          | /stop      | This method forwards a POST request to the monitoring agents on the worker nodes to stop the collection of system calls                                                  |
| ANY          | /proxy       | Acts as a proxy and allows the tool to access the Kubernetes API and retrieve information about the resources of the cluster                                                |