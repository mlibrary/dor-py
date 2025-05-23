from fastapi import APIRouter, Body


packages_router = APIRouter(prefix="/packages")


@packages_router.post("/")
async def create_package(package_metadata: dict = Body(...)):
    print(package_metadata)
    return {}
