from fastapi import APIRouter, HTTPException
from models.form_models import Form
from db_handler import get_connection, close_connection
from routers.data_layer.forms import create_form, update_form, delete_form_from_db

router = APIRouter(prefix="/form_definitions", tags=["Forms"])


'''
This API implements endpoints used to work with form definitions.

For the moment, we only have mechanisms to create forms.
'''

@router.post("/forms", summary="Create a new form")
def create_or_update_form(form: Form, form_id: int = None):
    """
    Create a new form in the database, or update an existing one.

    Receives a JSON payload with the form details (key, name, description) and 
    inserts it into the database. Returns the newly created form details.
    If a form with the same key already exists, it updates its details instead.
    """

    # Determine if the input has a form_id (update) or not (create)
    try:
        if form_id:
        # UPDATE the form instead of creating a new one
            
            # Call update method in database layer
            updated_form = update_form(form_id, form)
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

    # conn = get_connection()
    # cursor = conn.cursor()

    # try:
    #     # First check if the form exists
    #     cursor.execute('SELECT id FROM form_definition.forms WHERE id = %s;', (form_id,))
    #     if not cursor.fetchone():
    #         raise HTTPException(status_code=404, detail=f"Form with id={form_id} not found")
        
    #     # If it exists, delete it
    #     cursor.execute('DELETE FROM form_definition.forms WHERE id = %s;', (form_id,))

    #     # Commit change
    #     conn.commit()

    #     return{"status": "success", "message": f"Form with id={form_id} deleted"}
    
    # # if an exception occurs
    # except HTTPException:
    #     raise

    # except Exception as e:
    #     conn.rollback()
    #     raise HTTPException(status_code=500, detail=str(e))
    
    # finally:
    #     cursor.close()
    #     close_connection()