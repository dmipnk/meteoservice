FROM ubuntu:latest
COPY . /meteoservice
WORKDIR /meteoservice
RUN ["apt","update","-y"]
RUN ["apt","install","pipx","-y"]
RUN ["pipx","install","poetry"]
RUN ["/root/.local/bin/poetry","install"]
RUN ["/root/.local/bin/poetry","run","python3","manage.py","collectstatic","--noinput"]
RUN ["/root/.local/bin/poetry","run","python3","manage.py","makemigrations"]
RUN ["/root/.local/bin/poetry","run","python3","manage.py","migrate"]
RUN ["/root/.local/bin/poetry","run","python3","manage.py","createsuperuser","--noinput"]
EXPOSE 9999
ENTRYPOINT ["/root/.local/bin/poetry","run","gunicorn","meteoservice.wsgi:application", "--bind", "0.0.0.0:9999", "--conf" ,"gunicorn.conf.py"] 

 



