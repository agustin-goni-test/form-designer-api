from fastapi import APIRouter, HTTPException
from models.form_models import Form
from db_handler import get_connection, close_connection 

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

    # Get the connection to the database
    conn = get_connection()

    # Create a cursor
    cursor = conn.cursor()

    
    try:
        if form_id:
            # UPDATE the form instead of creating a new one
            
            # First check if the form exists
            cursor.execute('SELECT id FROM form_definition.forms WHERE id = %s;', (form_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Form with id={form_id} not found")
            
            # If it exists, update it
            cursor.execute('''
                UPDATE form_definition.forms
                SET key = %s,
                    name = %s,
                    description = %s,
                    updated_at = now()
                WHERE id = %s
                RETURNING id, key, name, description, created_at, updated_at;
            ''', (form.key, form.name, form.description, form_id))

            # Load updated form
            updated_form = cursor.fetchone()

            # Commit the transaction
            conn.commit()

            # Return info
            return{"status": "success", "form": updated_form}

        else:
            # INSERT a new form

            # Use cursor to insert the form into the database
            cursor.execute('''
                INSERT INTO form_definition.forms (key, name, description, created_at, updated_at)
                VALUES (%s, %s, %s, now(), now())
                RETURNING id, key, name, description, created_at;
            ''', (form.key, form.name, form.description))

            # Get the newly created form (for the response)
            new_form = cursor.fetchone()

            # Commit the transaction
            conn.commit()

            # Return the new form details
            return{"status": "success", "form": new_form}
    
    # If an exception occurs
    except HTTPException:
        raise

    except Exception as e:
        # Rollback the transaction
        conn.rollback()

        # Raise an HTTP exception
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Close the cursor and connection
        cursor.close()
        close_connection()



@router.delete("/forms/{form_id}", summary="Delete a form")
def delete_form(form_id: int):
    '''
    Delete a form from the database.

    Receives the form ID in the URL and deletes the corresponding form.
    Returns a success message if deletion was successful.
    '''

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # First check if the form exists
        cursor.execute('SELECT id FROM form_definition.forms WHERE id = %s;', (form_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Form with id={form_id} not found")
        
        # If it exists, delete it
        cursor.execute('DELETE FROM form_definition.forms WHERE id = %s;', (form_id,))

        # Commit change
        conn.commit()

        return{"status": "success", "message": f"Form with id={form_id} deleted"}
    
    # if an exception occurs
    except HTTPException:
        raise

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        cursor.close()
        close_connection()