FROM oraclelinux:8-slim
RUN microdnf install yum gcc-c++ python3-devel vim dos2unix
RUN python3 -m pip install requests html_to_json django firebase-admin kubernetes
# RUN mkdir -p /opt/share/app
# RUN chmod 777 /opt/share/app
#COPY src/ /opt/share/app
COPY src/ /opt/
EXPOSE 8000/tcp
# CMD ["/opt/share/app/manage.py","runserver", "0.0.0.0:8000"]
CMD ["python3", "/opt/manage.py", "runserver", "0.0.0.0:8001"]
