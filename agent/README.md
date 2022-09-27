# Agent

Each Worker node can have a monitoring agent (also referred to as a “probe”) running in the background whose job is to collect system calls and transfer them to the external machine that is running the µDetector tool through Websockets. It is written in Python using the Flask web framework.


### Agent API
| Method | URL              | Description                                                                                                                                 |
|---------------|----------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| GET           | /                       | This method always returns 200 and is used to verify that the connection to the agent is working                                                                                                      |
| GET           | /start         | This method spawns a sysdig process with the parameters from the request data such as filters and args. The system calls collected by this process are then piped to another process responsible for sending them over the network using websockets to the µDetector tool. Before they are sent, the system calls are grouped in batches defined by a configurable window size which defaults to 5 seconds. This means that every 5 seconds a batch of system calls is sent through over websockets          |
| POST           | /stop         | This method stops the sysdig and websocket processes that were spawned by the agent in the /start method where the purpose is to stop the collection of system calls |
