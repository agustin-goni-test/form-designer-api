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


def update_form(form_id: int, form: Form):
    """
    Handle updating an existing form in the database.

    Takes a form ID and a Form object as input.
    Updates the corresponding form in the database.
    Returns the updated form details.
    """

    # Get the connection to the database
    conn = get_connection()

    # Create a cursor
    cursor = conn.cursor()

    try:
        # Check if the form with the given ID exists
        cursor.execute('SELECT id FROM form_definition.forms WHERE id = %s;', (form_id,))
        existing_form = cursor.fetchone()

        if existing_form is None:
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