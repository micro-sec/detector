FROM docker.io/sysdig/sysdig
RUN yum install python3.8 -y
ADD requirements.txt /detector/requirements.txt
WORKDIR /detector
RUN pip3 install -r requirements.txt
ADD setup.py /detector/setup.py
ADD agent /detector/agent
ADD daemon /detector/daemon
ADD detector /detector/detector
RUN pip3 install -e .
