from db_handler import get_connection, close_connection
from models.form_models import FormVersion
import json
from logger import get_logger

# Initialize logger
logger = get_logger(__name__)


def create_form_version(form_id: int, form_version: FormVersion):
    '''
    Method to create a new vresion of the form in the database.
    
    It uses the next available version number for this particular form
    (1 if there is no previous version)
    '''
    logger.info(f"Starting version creation...")

    # Get the connection
    conn = get_connection()
    
    # Create a cursor
    cursor = conn.cursor()

    try:
        # Find the next version number to use
        next_version = _find_next_version_number(form_id, conn)
        logger.info(f"Next version to be created for form {form_id} is {next_version}")

        # Update input with correct version number
        form_version.version_number = next_version

        # Insert the new version in the database
        cursor.execute('''
            INSERT INTO form_definition.form_versions (
                       form_id,
                       version_number,
                       key,
                       schema,
                       is_active,
                       created_at,
                       updated_at)
            VALUES (%s, %s, %s, %s, True, now(), now())
            RETURNING *
        ''', (form_id,
              form_version.version_number,
              form_version.key,
              json.dumps(form_version.schema),
              ))

        # Fetch the newly created form version and row id
        new_version = cursor.fetchone()
        new_id = new_version['id']

        # Commit the transaction
        conn.commit()

        # Log the result
        logger.info(f"Row with id={new_id} created to store version {next_version} of form {form_id}")

        # Return the new form version details
        return {"status": "Version created successfully",
                "form_version": new_version}

    except Exception as e:
        logger.error(f"Error creating form version: {str(e)}")
        conn.rollback()
        raise Exception(f"Error creating form version for form {form_id}")

    finally:
        logger.info("Ending execution of version creation (success or failure)...")
        cursor.close()
        close_connection()


def _find_next_version_number(form_id: int, conn) -> int:
    '''Find the next available version number for this form.'''
    cursor = conn.cursor()

    try:
        # Find next version number
        cursor.execute('''
            SELECT COALESCE(MAX(version_number), 0) + 1 AS next_version
            FROM form_definition.form_versions
            WHERE form_id = %s;
        ''', (form_id,))

        # Obtain result (next version) and return
        result = cursor.fetchone()
        return result['next_version']

    except Exception as e:
        raise Exception(f"Error finding next version number: {str(e)}")

    finally:
        cursor.close()