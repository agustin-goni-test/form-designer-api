from db_handler import get_connection, close_connection
from fastapi import HTTPException
from models.component_models import ComponentVersion
import json
from logger import get_logger

logger = get_logger(__name__)

def create_component_version(component_version: ComponentVersion):
    """
    Handle creation of new component version in the database.

    Takes a ComponentVersion object as input and inserts it into the database.
    Returns the newly created component version details.
    """

    # Log the start of the process
    logger.info("Starting component version creation.")

    # Get the connection to the database
    conn = get_connection()

    # Create a cursor
    cursor = conn.cursor()

    try:
        # Find next version number
        next_version_number = _find_next_version_number(component_version.component_id, conn)
        logger.debug(f"Next version number for component ID {component_version.component_id} is {next_version_number}") 
        
        # Update input with the correct next version number. If the user provided one, ignore it.
        component_version.version_number = next_version_number

        definition = {
            "default_props": component_version.default_props or {},
            "validation_config": component_version.validation_config or {},
            "service_bindings": component_version.service_bindings or {}
        }
        
        logger.debug(f"Component definition to be inserted: {definition}")

        # Insert the new component version into the database
        cursor.execute('''
            INSERT INTO form_definition.component_versions (
                       component_id,
                       version_number,
                       definition,
                       default_props,
                       validation_config,
                       service_bindings,
                       is_active,
                       created_at,
                       updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, True, now(), now())
            RETURNING id, component_id, version_number, definition,
                       default_props, validation_config, service_bindings, is_active, created_at, updated_at;
        ''', (component_version.component_id,
              component_version.version_number,
              json.dumps(definition),
              json.dumps(component_version.default_props),
              json.dumps(component_version.validation_config),
              json.dumps(component_version.service_bindings), 
              ))

        # Fetch the newly created component version
        new_component_version = cursor.fetchone()

        # Commit the transaction
        conn.commit()

        # Log the result of the creation
        logger.info(f"Successfully created component version with ID: {new_component_version['id']}")

        # Return the new component version details
        return new_component_version

    # If an exception occurs
    except Exception as e:
        # Log error
        logger.error(f"Error creating component version: {str(e)}, exc_info=True")

        # Rollback the transaction in case of error
        conn.rollback()

        # Raise the exception to be handled by the caller
        raise Exception(f"Error creating component version: {str(e)}")
    
    finally:
        # Close the cursor and connection
        cursor.close()
        close_connection()
        logger.debug("Database connection closed.")


# Internal helper to find next version number
def _find_next_version_number(component_id: int, conn) -> int:
    '''Find the next available version number for a given component ID.'''
    cursor = conn.cursor()
    try:
        # Find next version number
        cursor.execute('''
            SELECT COALESCE(MAX(version_number), 0) + 1 AS next_version
            FROM form_definition.component_versions
            WHERE component_id = %s;
        ''', (component_id,))
        result = cursor.fetchone()
        return result['next_version']
    
    # If there is an error, raise exception
    except Exception as e:
        raise Exception(f"Error finding next version number: {str(e)}")
    
    finally:
        cursor.close()


def update_component_version(component_version: ComponentVersion):
    """
    Handle updating an existing component version in the database.

    Takes a component version ID and a ComponentVersion object as input.
    Updates the corresponding component version in the database.
    Returns the updated component version details.
    """

    # Log the start of the process
    logger.info(f"Starting update for component id {component_version.component_id} with version number: {component_version.version_number}")

    # Validate if version number is present, otherwise raise error
    version_number = component_version.version_number
    if not version_number:
        error_msg = "Component version number must be provided for update."
        logger.error(error_msg)
        raise Exception(error_msg)

    # Get the connection to the database
    conn = get_connection()

    # Create a cursor
    cursor = conn.cursor()

    try:
        definition = {
            "default_props": component_version.default_props or {},
            "validation_config": component_version.validation_config or {},
            "service_bindings": component_version.service_bindings or {}
        }

        logger.debug(f"Component definition to be updated: {definition}")

        # Update the existing component version in the database
        # Active status does not change.
        # Version number does not change either (it's an update, not a new version).
        cursor.execute('''
            UPDATE form_definition.component_versions
            SET component_id = %s,
                version_number = %s,
                definition = %s,
                default_props = %s,
                validation_config = %s,
                service_bindings = %s,
                is_active = true,
                updated_at = now()
            WHERE id = %s
            RETURNING id, component_id, version_number, definition,
                      default_props, validation_config, service_bindings, is_active, created_at, updated_at;
        ''', (component_version.component_id,
              component_version.version_number,
              json.dumps(definition),
              json.dumps(component_version.default_props),
              json.dumps(component_version.validation_config),
              json.dumps(component_version.service_bindings),
              component_version.id))

        # Fetch the updated component version
        updated_component_version = cursor.fetchone()

        # Commit the transaction
        conn.commit()

        # Log the result of the update
        logger.info(f"Successfully updated component version with ID: {updated_component_version['id']}")

        # Return the updated component version details
        return updated_component_version

    # If an exception occurs
    except Exception as e:
        # Log error
        logger.error(f"Error updating component version ID {version_id}: {str(e)}", exc_info=True)

        # Rollback the transaction in case of error
        conn.rollback()

        # Raise the exception to be handled by the caller
        raise Exception(f"Error updating component version: {str(e)}")
    
    finally:
        # Close the cursor and connection
        cursor