#!/usr/bin/env python

import os

from gateway.ocfl_repository_gateway import OcflRepositoryGateway

storage_path = os.environ.get("STORAGE_PATH")

if not (storage_path and storage_path.strip()):
    raise Exception("Environment variable STORAGE_PATH is not set")

if not os.path.exists(storage_path) or not os.listdir(storage_path):
    OcflRepositoryGateway(storage_path=storage_path).create_repository()  
    print(f"Created OCFL repository at {storage_path}")

print(f"OCFL repository at {storage_path}")
