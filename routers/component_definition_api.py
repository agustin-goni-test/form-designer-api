from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/component_definitions", tags=["Components"])

@router.get("/test", summary="Test endpoint for component definitions")
def test_component_endpoint():
    """
    A simple test endpoint to verify that the component definitions router is working.
    """
    return {"status": "Component definitions API is operational."}

