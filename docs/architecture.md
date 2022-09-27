# Architecture

The architecture here described represents a more generalized view of the µDetector tool and how it interacts with the other systems.

![Architecture](/docs/architecture.png "Architecture")

The µDetector tool interacts with Kubernetes clusters using different technologies. When we refer to the Kubernetes cluster, we also include support for KubeEdge meaning that edge nodes can also be monitored. The communication between the Edge and the Cloud is made through the KubeEdge components CloudCore and EdgeCore.

Firstly, to obtain information about the cluster, such as the pods and nodes that are running on the system, and be able to deploy the sysdig probes in the correct nodes, it is necessary to run a Daemon on the master node that will communicate with the tool through REST. Then the user can specify in a JSON file configurations of how the tool should behave when running. For example, the user can specify the services he wants to monitor, the format in which the system calls are collected, the size of the window of collection of system calls and whether the system calls are compressed or not. The configuration file is then validated by the tool and the instructions are sent to the master node (through the daemon) which is responsible for communicating with the monitoring agents (also referred to as “probes"). These monitoring agents will then run an instance of sysdig to retrieve the system calls and transfer them to the machine that is running the µDetector tool where they are temporarily stored in a Redis instance for later use by the IDS module. After the system calls are being monitored (i.e.: extracted from the worker nodes and transferred to the machine that is running the µDetector tool), the user can spawn intrusion detection instances by providing a configuration file in a JSON format. The configuration file requires a type (training or detection), an algorithm (for example BoSC or STIDE) and a duration (in seconds). When an Intrusion Detection instance is running, the IDS module is responsible for analyzing the system calls according to a certain algorithm and generating a profile if it is a training phase or generating alarms if it is the detection phase and anomalous behavior is detected.

The µDetector tool has two user components that ease the interaction of the user with the tool and improve the observability of the system. These are the CLI and the Web Dashboard. The API Server and the IDS are operations components because they do not interact directly with the user and are responsible instead for the inner workings of the tool.

Below we find a screenshot of the main page of µDetector tool.

![Dashboard](/docs/dashboard.png "Dashboard")