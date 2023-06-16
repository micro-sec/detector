# Deploy instructions

- To deploy the container:
    ```shell
    docker build . -f deploy/Dockerfile -t detector
    ```

- To deploy in a Kubernetes cluster (one agent per node, one daemon, one detector, one database)
    - Deploy the container in all nodes;
    - Apply the manifest:
        ```shell
        kubectl apply -f deploy/detector.yml -n detector
        ```
    - Wait a while until the setup completes;
    - The dashboard is available through NodePort 31000 (i.e, `<some_node_ip>:31000`).
    - To destroy the cluster:
        ```shell
        kubectl delete -f deploy/detector.yml -n detector
        ```
