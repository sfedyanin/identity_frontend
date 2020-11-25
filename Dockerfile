FROM ubuntu:18.04

MAINTAINER dan.vagg@vadix.io

RUN apt-get update && \
	apt-get install -y \
        curl wget vim \
		python3 python3-virtualenv \
		python3-pip libxml2-dev libxslt1-dev \
		libsasl2-dev python3-dev libldap2-dev libssl-dev \
        graphviz libgraphviz-dev

WORKDIR /opt/vdx_id

COPY vdx_id/requirements.txt /opt/vdx_id/requirements.txt
RUN pip3 install -r /opt/vdx_id/requirements.txt

COPY vdx_id/requirements_delta.txt /opt/vdx_id/requirements_delta.txt
RUN pip3 install -r /opt/vdx_id/requirements_delta.txt

COPY vdx_id /opt/vdx_id
WORKDIR /opt/vdx_id

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
