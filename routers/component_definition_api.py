from fastapi import APIRouter, HTTPException
from models.component_models import Component
from db_handler import get_connection, close_connection
from routers.data_layer.components import create_component, update_component, get_component_by_id, list_components_from_db, delete_component_from_db

router = APIRouter(prefix="/component_definitions", tags=["Components"])

@router.get("/test", summary="Test endpoint for component definitions")
def test_component_endpoint():
    """
    A simple test endpoint to verify that the component definitions router is working.
    """
    return {"status": "Component definitions API is operational."}


@router.post("/components", summary="Create or update a component definition")
def create_or_update_component(component: Component, component_id: int = None):
    '''
    Endpoint to create or update a component definition.
    '''
    try:
        if component_id:
            # Update existing component logic here
            updated_component = update_component(component_id, component)

            # Return info
            return {"status": "Component updated", "component_id": component_id, "component": component}
        
        else:
            # Create new component logic here
            new_component = create_component(component)
            
            # Return info
            return {"status": "Component created", "component": new_component}
    
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing component: {str(e)}")


@router.get("/components/{component_id}", summary="Retrieve a component definition by ID")
def get_component(component_id: int):
    '''
    Endpoint to retrieve a component definition by its ID.
    '''
    try:
        # Get the component by ID
        component = get_component_by_id(component_id)
        
        # return component details
        return component
    
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving component: {str(e)}")
    

@router.get("/components", summary="List all component definitions")
def list_components():
    '''
    Endpoint to list all component definitions.
    '''
    try:
        components = list_components_from_db()
        return {"status": "success", "components": components}

    except HTTPException as e:
        raise
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing components: {str(e)}")


@router.delete("/components/{component_id}", summary="Delete a component definition by ID")
def delete_component(component_id: int):
    '''
    Endpoint to delete a component definition by its ID.
    '''
    try:
        # Deletion logic here
        # Assuming a delete_component_from_db function exists in the data layer
        message = delete_component_from_db(component_id)
        return message
    
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting component: {str(e)}")        # Raise the exception to be handled by the caller



