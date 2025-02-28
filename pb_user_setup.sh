#!/bin/bash

# Wait until PocketBase is fully initialized and running
echo "Waiting for PocketBase to initialize..."
until nc -z localhost 8080; do
  sleep 2
done

echo "Creating superuser..."
/pb/pocketbase superuser upsert test@umich.edu testumich
