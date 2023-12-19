FROM python:3.11
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD ["bash", "-c", "python cron.py 5 & uvicorn views:app --host 0.0.0.0 --port $PORT"]