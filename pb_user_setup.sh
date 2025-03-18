#!/bin/bash

# Wait until PocketBase is fully initialized and running
echo "Waiting for PocketBase to initialize..."
for i in {1..10}; do
    if nc -z localhost 8080; then
        break
    fi
    sleep 2
done

if ! nc -z localhost 8080; then
    echo "PocketBase failed to initialize within the expected time."
    exit 1
fi

echo "Creating superuser..."
/pb/pocketbase superuser upsert test@umich.edu testumich