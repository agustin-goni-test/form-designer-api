from models.form_models import Form
from db_handler import get_connection, close_connection
from fastapi import HTTPException

def create_form(form: Form):
    """
    Handle creation of new form in the database.

    Takes a Form object as input and inserts it into the database.
    Returns the newly created form details.
    """

    # Get the connection to the database
    conn = get_connection()

    # Create a cursor
    cursor = conn.cursor()

    try:
        # Insert the new form into the database
        cursor.execute('''
            INSERT INTO form_definition.forms (key, name, description, created_at, updated_at)
            VALUES (%s, %s, %s, now(), now())
            RETURNING id, key, name, description, created_at, updated_at;
        ''', (form.key, form.name, form.description))

        # Fetch the newly created form
        new_form = cursor.fetchone()

        # Commit the transaction
        conn.commit()

        # Return the new form details
        return new_form

    # If an exception occurs
    except Exception as e:
        # Rollback the transaction in case of error
        conn.rollback()

        # Raise the exception to be handled by the caller
        raise Exception(f"Error creating form: {str(e)}")
    
    finally:
        # Close the cursor and connection
        cursor.close()
        close_connection()


def update_form(form_id: int, udpate_key: bool, form: Form):
    """
    Handle updating an existing form in the database.

    Takes a form ID and a Form object as input.
    Updates the corresponding form in the database.
    Returns the updated form details.

    Parameter update_key indicates whether to update the 'key' field or keep the existing one.
    """

    # Get the connection to the database
    conn = get_connection()

    # Create a cursor
    cursor = conn.cursor()

    try:
        # Check if the form with the given ID exists
        cursor.execute('SELECT id, key FROM form_definition.forms WHERE id = %s;', (form_id,))
        existing_form = cursor.fetchone()

        if existing_form is None:
            raise HTTPException(status_code=404, detail=f"Form with id={form_id} not found")
        
        new_key = form.key if udpate_key else existing_form['key']
        
        # If it exists, update it
        cursor.execute('''
            UPDATE form_definition.forms
            SET key = %s,
                name = %s,
                description = %s,
                updated_at = now()
            WHERE id = %s
            RETURNING id, key, name, description, created_at, updated_at;
        ''', (new_key, form.name, form.description, form_id))

        # Load updated form
        updated_form = cursor.fetchone()

        # Commit the transaction
        conn.commit()

        # Return info
        return updated_form

    # If an exception occurs
    except HTTPException:
        raise

    except Exception as e:
        # Rollback the transaction
        conn.rollback()

        # Raise an exception to be handled by the caller
        raise Exception(f"Error updating form: {str(e)}")
    
    finally:
        # Close the cursor and connection
        cursor.close()
        close_connection()


# Method name needs to be different from the router method name
def delete_form_from_db(form_id: int):
    '''
    Delete a form from the database.

    Receives the form ID and deletes the corresponding form.
    Returns a success message if deletion was successful.
    '''

    # Create connectio and cursor
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # First check if the form exists
        cursor.execute('SELECT id FROM form_definition.forms WHERE id = %s;', (form_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Form with id={form_id} not found")
        
        # If it exists, delete it
        cursor.execute('DELETE FROM form_definition.forms WHERE id = %s;', (form_id,))

        # Commit changes
        conn.commit()

        return {"status": "success", "message": f"Form with id={form_id} deleted"}

    except HTTPException:
        raise

    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting form: {str(e)}")

    finally:
        # Close cursor and connection
        cursor.close()
        close_connection()


def get_form_from_db(form_id: int):
    '''
    Retrieve form details from the database.

    Receives the form ID and returns the corresponding form details.
    '''

    # Get the connection to the database
    conn = get_connection()

    # Create a cursor
    cursor = conn.cursor()

    try:
        # Fetch the form with the given ID
        cursor.execute('SELECT id, key, name, description, created_at, updated_at FROM form_definition.forms WHERE id = %s;', (form_id,))
        form = cursor.fetchone()

        if form is None:
            raise HTTPException(status_code=404, detail=f"Form with id={form_id} not found")

        return {"status": "success", "form": form}

    except HTTPException:
        raise

    except Exception as e:
        # Raise an HTTP exception
        raise HTTPException(status_code=500, detail=f"Error retrieving form: {str(e)}")
    
    finally:
        # Close the cursor and connection
        cursor.close()
        close_connection()


def list_forms():
    '''
    List all forms in the database.

    Returns a list of all forms with their details.
    '''

    # Get the connection to the database
    conn = get_connection()

    # Create a cursor
    cursor = conn.cursor()

    try:
        # Fetch all forms
        cursor.execute('SELECT id, key, name, description, created_at, updated_at FROM form_definition.forms;')
        forms = cursor.fetchall()

        return {"status": "success", "forms": forms}

    except Exception as e:
        # Raise an HTTP exception
        raise HTTPException(status_code=500, detail=f"Error listing forms: {str(e)}")
    
    finally:
        # Close the cursor and connection
        cursor.close()
        close_connection()