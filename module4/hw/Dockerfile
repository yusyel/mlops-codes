FROM agrigorev/zoomcamp-model:mlops-3.9.7-slim

RUN pip install -U pip
RUN pip install pipenv

WORKDIR /app


COPY starter.py ./
COPY ["Pipfile", "Pipfile.lock", "./"]

RUN pipenv install --system --deploy


ENTRYPOINT [ "python3", "/app/starter.py" ]