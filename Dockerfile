FROM oraclelinux:8-slim
RUN microdnf install yum gcc-c++ python39 vim dos2unix
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3.9 get-pip.py
RUN python3.9 -m pip install requests html_to_json django firebase-admin kubernetes uuid email==6.0.0a1
COPY src/ /opt/
EXPOSE 8000/tcp
CMD ["python3.9", "/opt/manage.py", "runserver", "0.0.0.0:8001"]
