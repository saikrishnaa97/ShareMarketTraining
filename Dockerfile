FROM oraclelinux:8-slim
RUN microdnf install yum gcc-c++ python39 vim dos2unix
RUN python39 -m pip install requests html_to_json django firebase-admin kubernetes uuid
COPY src/ /opt/
EXPOSE 8000/tcp
CMD ["python3", "/opt/manage.py", "runserver", "0.0.0.0:8001"]
