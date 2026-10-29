FROM python:3.12-slim

WORKDIR /app

COPY app/requirements.txt ./app/requirements.txt
RUN pip install --no-cache-dir -r app/requirements.txt

COPY app ./app

RUN useradd --uid 1000 --create-home --shell /usr/sbin/nologin appuser && chown -R appuser:appuser /app
USER 1000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health').read()"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]