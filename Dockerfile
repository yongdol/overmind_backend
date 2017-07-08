# Pull image
FROM centos:latest
MAINTAINER Swalloow "joon920570@gmail.com"

# Running on image
RUN yum update -y
RUN yum install -y git epel-release gcc openssl-devel
RUN yum install -y python-pip python-dev python-devel build-essential python-virtualenv
RUN yum install -y supervisor pwgen bash-completion psmisc net-tools
RUN yum install -y mysql-server mysql
RUN yum clean all

# Clone project
#COPY . /Friskweb-API
#WORKDIR /Friskweb-API

# Running on container
#RUN pip install -r requirements.txt
#ENTRYPOINT ["python"]
#CMD ["run.py"]
