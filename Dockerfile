FROM postgres:latest

WORKDIR /usr/src/app 

#ADD python-requirements.txt /usr/src/app/python-requirements.txt
#ADD db.py /usr/src/app/db.py

#ADD input_data/orb_branches.csv /usr/src/app/orb_branches.csv
#ADD input_data/orb_companies.csv /usr/src/app/orb_copanies.csv

#RUN apt-get update
#RUN apt-get install -y python-pip

#RUN pip install virtualenv
#RUN virtualenv -p python virtual

#RUN /usr/src/app/virtual/bin/pip install -r /usr/src/app/python-requirements.txt

#ENTRYPOINT ["/usr/src/app/virtual/bin/python", "/usr/src/app/db.py"]
