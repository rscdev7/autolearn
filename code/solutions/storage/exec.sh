uvicorn --host $HOST_NAME --port $SERVER_PORT --workers $WEB_SERVER_WORKERS main:app & 
python3 launch_guard.py
