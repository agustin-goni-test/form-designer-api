from db_handler import get_connection, close_connection
from models.form_models import FormVersion
import json
from logger import get_logger

# Initialize logger
logger = get_logger(__name__)


def create_form_version(form_id: int, form_version: FormVersion):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Find the next version number to use
        next_version = _find_next_version_number(form_id, conn)

        # Update input with correct version number

        # Insert the new version in the database

        # Fetch the newly created form version

        # Commit the transaction

        # Log the result

        # Return the new form version details
        pass

    except Exception as e:
        pass

    finally:
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
        pass

    finally:
        cursor.close()