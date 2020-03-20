FROM python:3.8

ENV DJANGO_SETTINGS_MODULE=CyadsProcessor.settings
ENV TOPIC_SUBSCRIPTION_NAME=dev
ENV PYTHONUNBUFFERED=1
ENV GOOGLE_TOPIC=development
ENV TOPIC_SUBSCRIPTION_NAME=dev
ENV GOOGLE_PROJECT_ID=asdas
ENV SECRET_KEY=asdas
ENV DEBUG=False
ENV DATABASE=cyads_processor
ENV DATABASE_HOST=localhost
ENV DATABASE_USER=root
ENV DATABASE_PASSWORD=root
ENV SECRET_KEY=asdas
RUN apt-get update && apt-get install -y ffmpeg
RUN rm -rf logs/*


COPY requirements.txt /opt/CyadsProcessor/requirements.txt
RUN pip3 install --no-cache-dir -r /opt/CyadsProcessor/requirements.txt

WORKDIR /opt/CyadsProcessor
COPY startup.sh .
RUN chmod +x startup.sh
COPY . /opt/CyadsProcessor

CMD ["/opt/CyadsProcessor/startup.sh"]


