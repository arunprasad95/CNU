FROM python
RUN apt-get update && apt-get -y install mysql-client 
COPY . /root
WORKDIR /root
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["sh","/root/run.sh"]
