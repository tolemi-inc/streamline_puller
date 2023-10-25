#CONTAINER TEMPLATE
FROM python:3.9-slim-bookworm

RUN echo $PATH

WORKDIR /opt/SCRIPT_NAME

#install requirements
COPY requirements.txt /opt/SCRIPTNAME
RUN pip install -r requirements.txt

# copy the script
COPY SCRIPT_NAME /opt/SCRIPT_NAME

# add the script callers to path
ENV PATH="/opt/zillow_puller/bin:$PATH"