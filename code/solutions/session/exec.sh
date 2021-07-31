uvicorn --host $HOST_NAME --port $SERVER_PORT --workers $WEB_SERVER_WORKERS main:app & 
python3 launch_update_guard.py &
python3 launch_record_guard.py