from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from models.form_models import FormVersion
from logger import get_logger
from routers.data_layer.form_versions import create_form_version, update_form_version 
from models.form_models import FormVersion

# Initialize logger
logger = get_logger(__name__)

# Initialize API router
router = APIRouter(prefix="/form_definitions", tags=["Component Versions"])

# Test method to ensure routing is working
@router.get("/test-versions", summary="Test endpoint for component versions")
def test_form_version_endpoint():
    """
    A simple test endpoint to verify that the component versions router is working.
    """
    # Log the test endpoint call
    logger.info("Form versions test endpoint called.")
    
    return {"status": "Forms versions API is operational."}


@router.post("/forms/{form_id}/versions", summary="Create a new form version")
@router.post("/forms/{form_id}/versions/{version_id}", summary="Update a specific version of a form")
def create_or_update_form_version(form_id: int,
                                  form_version: FormVersion,
                                  version_id: int = None):
    '''
    Method to create or update a form version.
    
    If the version number is provided, it will update the corresponding version.
    Else, it will create a new version.'''

    # Determine if it's a creation or update operation
    update_version = True if version_id else False

    try:
        if update_version:
            # Log the update operation
            logger.info(f"Attempting to update version {version_id} of form {form_id}")

            # Call database operation
            message = update_form_version(form_id, version_id, form_version)

            # Return message with status code 200 (OK)
            return JSONResponse(
                status_code = 200,
                content = {
                    "status": "Version updated successfully",
                    "data": jsonable_encoder(message)
                }
            )

        else:
            # Log the creation operation
            logger.info(f"Attempting to create a new version for form {form_id}")

            # Call database operation
            message = create_form_version(form_id, form_version)

            # Return message with explicit 201 status code (Created)
            return JSONResponse(
                status_code = 201,
                content = {
                    "status": "Version created successfully",
                    "data": jsonable_encoder(message)
                }
            )

    except HTTPException:
        logger.warning("HTTPException while creating or updating a form version")
        raise
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing form version: {str(e)}")