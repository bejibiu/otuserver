FROM centos:7
RUN yum install python3 -y
WORKDIR /app
COPY httpd.py /app/httpd.py
CMD ["/usr/bin/python3.6","/app/httpd.py","--host", "0.0.0.0"]
