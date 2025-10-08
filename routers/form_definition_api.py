from fastapi import APIRouter, HTTPException
from models.form_models import Form
from db_handler import get_connection, close_connection 

router = APIRouter(prefix="/form_definitions", tags=["Forms"])


'''
This API implements endpoints used to work with form definitions.

For the moment, we only have mechanisms to create forms.
'''

@router.post("/forms", summary="Create a new form")
def create_form(form: Form):
    """
    Create a new form in the database.

    Receives a JSON payload with the form details (key, name, description) and 
    inserts it into the database. Returns the newly created form details.

    PENDING:
    Implement a way to also update a form, with this same endpoint, by using the id.
    """

    # Get the connection to the database
    conn = get_connection()

    # Create a cursor
    cursor = conn.cursor()

    
    try:
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
    except Exception as e:
        # Rollback the transaction
        conn.rollback()

        # Raise an HTTP exception
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Close the cursor and connection
        cursor.close()
        close_connection()