from fastapi import APIRouter, HTTPException
from models.component_models import ComponentVersion
from routers.data_layer.component_versions import create_component_version, update_component_version
from routers.data_layer.component_versions import get_component_version_from_db, get_latest_component_version_from_db
from routers.data_layer.component_versions import get_all_versions_from_db
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
    if update_version:
        logger.info(f"Updating component version ID: {version_id} for component ID: {component_id}")
    else:
        logger.info(f"Creating new component version for component ID: {component_id}")

    try:
        if update_version:
            # Update existing component version logic here
            logger.info("Updating an existing version...")
            updated_version = update_component_version(component_id, version_id, component_version)

            return {"status": "Component version updated",
                    "version_number": component_version.version_number,
                    "component_version": updated_version}
            # return {"status": "OK"}
        
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
    

@router.get("/{component_id}/versions/{version_id}", summary="Obtain a particular version of a component")
def get_component_version(component_id: int, version_id: int):
    '''
    Endpoint to get a particular version of a component
    '''

    logger.info(f"Obtaining version {version_id} of component with id {component_id}")

    try:
        component = get_component_version_from_db(component_id, version_id)

        return {"status": "Component version obtained",
                "component_version": component}

    except HTTPException:
        logger.warning("HTTPException occurred while obtaining component version.")
        raise

    except Exception as e:
        logger.error(f"Error obtaining version {version_id} of component {component_id}: {str(e)}")



@router.get("/{component_id}/all-versions", summary="Obtain latest version of a component")
def get_version_list(component_id: int):
    '''
    Endpoint to get all versions for a component.
    '''

    logger.info(f"Getting all versions for component id {component_id}")

    try:
        versions = get_all_versions_from_db(component_id)

        return {"status": "Obtained all versions",
                "versions": versions }

    except HTTPException:
        logger.warning("HTTPException while obtaining all versions of the component.")

    except Exception as e:
        logger.error(f"Error obtaining version list for component {component_id}: {str(e)}")


@router.get("/{component_id}/versions", summary="Obtain latest version of a component")
def get_latest_version_from_db(component_id: int):
    '''
    Endpoint to obtain the latest version of a component
    '''

    logger.info(f"Obtaining latest version for component id {component_id}")

    try:
        component = get_latest_component_version_from_db(component_id)

        return {"status": "Component version obtained",
                "component": component}

    except HTTPException:
        logger.warning("HTTPException while obtaining the latest version...")
        raise

    except Exception as e:
        logger.error(f"Error obtaining latest version of component {component_id}: {str(e)}")

