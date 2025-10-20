from fastapi import APIRouter, HTTPException
from models.component_models import ComponentVersion
from routers.data_layer.component_versions import create_component_version, update_component_version
from logger import get_logger
from typing import Optional

# Initialize logger
logger = get_logger(__name__)

# Initialize the API router
router = APIRouter(prefix="/component_definitions/components", tags=["Component Versions"])

# Test method
@router.get("/test", summary="Test endpoint for component versions")
def test_component_version_endpoint():
    """
    A simple test endpoint to verify that the component versions router is working.
    """
    # Log the test endpoint call
    logger.info("Component versions test endpoint called.")
    
    return {"status": "Component versions API is operational."}


# @router.post("/versions", summary="Create or update new component version")
# def create_or_update_component_version(component_version: ComponentVersion):
#     '''
#     Endpoint to create or update a component version.

#     If the version number is included, the endpoint assumes it's an update operation
#     and updates the data for that particular component id and version.
#     If not, a new version is created with the next available version number.
#     '''

#     # Determine if the input has a version_number (update) or not (create)
#     update_version = True if component_version.version_number else False

#     # Log the start of the request
#     logger.info("Received request to create or update component version.")

#     try:
#         if update_version:
#             # Update existing component version logic here
#             # Placeholder for update logic
#             updated_version = update_component_version(component_version)

#             return {"status": "Component version updated",
#                     "version_number": component_version.version_number,
#                     "component_version": updated_version}
        
#         else:
#             # Log the start of the creation process
#             logger.info("Creating new component version.")
#             # Create new component version logic here
#             new_version = create_component_version(component_version)
#             logger.info(f"Component version successfully created with ID: {new_version['id']}")
#             # Return info
#             return {"status": "Component version created",
#                     "component_version": new_version}
    
#     except HTTPException:
#         logger.warning("HTTPException occurred while processing component version.")
#         raise

#     except Exception as e:
#         logger.error(f"Error processing component version: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=f"Error processing component version: {str(e)}")
    


@router.post("/{component_id}/versions", summary="Create a new component")
@router.post("/{component_id}/versions/{version_id}", summary="Update new component version")
def create_or_update_component_version(component_id: int, 
                                       component_version: ComponentVersion,
                                       version_id: Optional[int] = None):
    '''
    Endpoint to create or update a component version.

    If the version number is included, the endpoint assumes it's an update operation
    and updates the data for that particular component id and version.
    If not, a new version is created with the next available version number.
    '''

    # Determine if the input has a version_number (update) or not (create)
    update_version = True if version_id else False

    # Log the start of the request
    logger.info("Received request to create or update component version.")
    
    if update_version:
        logger.info(f"Updating component version ID: {version_id} for component ID: {component_id}")
    else:
        logger.info(f"Creating new component version for component ID: {component_id}")

    try:
        if update_version:
            # Update existing component version logic here
            # Placeholder for update logic
            # updated_version = update_component_version(component_version)

            # return {"status": "Component version updated",
            #         "version_number": component_version.version_number,
            #         "component_version": updated_version}
            logger.info("Updating an existing version...")
            return {"status": "OK"}
        
        else:
            # Log the start of the creation process
            logger.info("Creating new component version...")
            # Create new component version logic here
            new_version = create_component_version(component_id, component_version)
            logger.info(f"Component version successfully created with ID: {new_version['id']}")
            # Return info
            return {"status": "Component version created",
                    "component_version": new_version}
            # return {"status": "OK"}
    
    except HTTPException:
        logger.warning("HTTPException occurred while processing component version.")
        raise

    except Exception as e:
        logger.error(f"Error processing component version: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing component version: {str(e)}")
    


