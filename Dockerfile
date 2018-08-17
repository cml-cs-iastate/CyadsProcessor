FROM python:3

COPY . /opt/CyadsProcessor
WORKDIR /opt/CyadsProcessor
RUN rm -rf logs/*

RUN pip3 install gunicorn
RUN pip3 install -r requirements.txt
RUN mkdir /opt/.key


ENV DJANGO_SETTINGS_MODULE=CyadsProcessor.settings
ENV TOPIC_SUBSCRIPTION_NAME=dev
ENV PYTHONUNBUFFERED=1
ENV GOOGLE_TOPIC=development
ENV GOOGLE_PROJECT_ID=asdas
ENV GOOGLE_APPLICATION_CREDENTIALS=/opt/CyadsProcessor
ENV SECRET_KEY=asdas
ENV DEBUG=False
ENV DATABASE=cyads_processor
ENV DATABASE_HOST=localhost
ENV DATABASE_USER=root
ENV DATABASE_PASSWORD=root


EXPOSE 8000

RUN chmod +x /opt/CyadsProcessor/startup.sh

CMD ["/opt/CyadsProcessor/startup.sh"]


