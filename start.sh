#!/bin/bash
chmod +x start.sh
exec uvicorn FMCBot:app --host 0.0.0.0 --port $PORT
