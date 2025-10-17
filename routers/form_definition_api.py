from fastapi import APIRouter, HTTPException
from models.form_models import Form
from db_handler import get_connection, close_connection
from routers.data_layer.forms import create_form, update_form, delete_form_from_db, get_form_from_db, list_forms    

router = APIRouter(prefix="/form_definitions", tags=["Forms"])


'''
This API implements endpoints used to work with form definitions.

For the moment, we only have mechanisms to create forms.
'''

@router.post(
        "/forms",
        summary="Create a new form",
        response_description="The created or updated form details",
        status_code=201
        )
def create_or_update_form(
    form: Form, 
    form_id: int = None, 
    update_key: bool = False
    ):
    """
    Create a new form in the database, or update an existing one.

    Receives a JSON payload with the form details (key, name, description) and 
    inserts it into the database. Returns the newly created form details.
    If a form with the same key already exists, it updates its details instead.

    **Parameters:**
    - **form**: The form details to create or update.
    - **form_id**: (Optional) The ID of the form to update. If not provided, a new form will be created.
    - **update_key**: (Optional) A boolean indicating whether to update the 'key' field of the form when updating.

    **Returns:**
    - **status**: A message indicating success.
    - **form**: The details of the created or updated form.

    **Raises:**
    - **HTTPException 400**: If form validation fails.
    - **HTTPException 500**: If there is a database error.
    """

    # Determine if the input has a form_id (update) or not (create)
    try:
        if form_id:
        # UPDATE the form instead of creating a new one
            
            # Call update method in database layer
            updated_form = update_form(form_id, update_key, form)
            # Return info
            return{"status": "success", "form": updated_form}
               
        else:
            # INSERT a new form

            # Call creation method in database layer
            new_form = create_form(form)
            return {"status": "success", "form": new_form}
        
    except HTTPException:
        raise

    except Exception as e:
        # Raise an HTTP exception
        raise HTTPException(status_code=500, detail=f"Database operation failed: {str(e)}")
                



@router.delete("/forms/{form_id}", summary="Delete a form")
def delete_form(form_id: int):
    '''
    Delete a form from the database.

    Receives the form ID in the URL and deletes the corresponding form.
    Returns a success message if deletion was successful.
    '''

    try:
        # Call deletion method in database layer
        message = delete_form_from_db(form_id)
        return message
    
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database operation failed: {str(e)}")

@router.get("/forms/{form_id}", summary="Get form details")
def get_form(form_id: int):
    '''
    Retrieve form details from the database.

    Receives the form ID in the URL and returns the corresponding form details.
    '''

    try:
        # Call retrieval method in database layer
        message = get_form_from_db(form_id)
        return message
    
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database operation failed: {str(e)}")
    

@router.get("/forms", summary="Health check endpoint")
def get_all_forms():
    '''
    Endpoint to get a list of all the forms in the database.
    ''' 

    try:
        message = list_forms()
        return message
    
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database operation failed: {str(e)}") 
