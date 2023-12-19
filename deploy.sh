. .env
bash -c python cron.py 5 & uvicorn views:app --host 0.0.0.0 --port $PORT