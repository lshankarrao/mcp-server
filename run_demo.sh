#!/bin/bash

echo "Starting MCP Weather App Demo"
echo "============================="

echo ""
echo "Starting MCP Server..."
cd server
python main.py &
SERVER_PID=$!
cd ..

echo "Waiting for server to start..."
sleep 5

echo ""
echo "Starting React Client..."
cd client
npm run dev &
CLIENT_PID=$!
cd ..

echo ""
echo "Demo started successfully!"
echo ""
echo "Server: http://localhost:8000"
echo "Client: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the demo..."

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping demo..."
    kill $SERVER_PID 2>/dev/null
    kill $CLIENT_PID 2>/dev/null
    echo "Demo stopped."
    exit 0
}

# Set trap to catch Ctrl+C
trap cleanup SIGINT

# Wait for user to stop
wait
