#CONTAINER TEMPLATE
FROM python:3.9-slim-bookworm

RUN echo $PATH

WORKDIR /opt/streamline_puller

#install requirements
COPY requirements.txt /opt/streamline_puller
RUN pip install -r requirements.txt

# copy the script
COPY streamline_puller /opt/streamline_puller

# add the script callers to path
ENV PATH="/opt/streamline_puller/bin:$PATH"