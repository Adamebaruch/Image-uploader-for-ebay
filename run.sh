#!/bin/bash
# Start backend
cd backend
source venv/bin/activate
python3 app.py &
BACKEND_PID=$!

# Start frontend server
cd ../frontend
python3 -m http.server 8080 &
FRONTEND_PID=$!

echo "Servers started. Press Ctrl+C to stop both servers."
wait $BACKEND_PID $FRONTEND_PID