from db_handler import get_connection, close_connection
from fastapi import HTTPException
from models.component_models import ComponentVersion
import json
from logger import get_logger

logger = get_logger(__name__)

def create_component_version(component_id: int, component_version: ComponentVersion):
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
        next_version_number = _find_next_version_number(component_id, conn)
        logger.debug(f"Next version number for component ID {component_id} is {next_version_number}") 
        
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
        ''', (component_id,
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


# Method to update a component version
def update_component_version(component_id: int,
                             version_number: int,
                             component_version: ComponentVersion):
    """
    Handle updating an existing component version in the database.

    Takes a component version ID and a ComponentVersion object as input.
    Updates the corresponding component version in the database.
    Returns the updated component version details.
    """

    # Log the start of the process
    logger.info(f"Starting update for component id {component_id} with version number: {version_number}")

    # Validate if version number is present, otherwise raise error
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

        # Get id of the record to update
        record_id = _get_record_id(component_id, version_number, conn)
        logger.debug(f"Record ID to be updated: {record_id}")

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
        ''', (component_id,
              version_number,
              json.dumps(definition),
              json.dumps(component_version.default_props),
              json.dumps(component_version.validation_config),
              json.dumps(component_version.service_bindings),
              record_id))

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
        logger.error(f"Error updating component version ID {component_version.id}: {str(e)}", exc_info=True)

        # Rollback the transaction in case of error
        conn.rollback()

        # Raise the exception to be handled by the caller
        raise Exception(f"Error updating component version: {str(e)}")
    
    finally:
        # Close the cursor and connection
        cursor.close()
        close_connection()


# Helper method to get record ID
def _get_record_id(component_id: int, version_number: int, conn) -> int:
    '''
    Internal helper to get the database record ID for a given component ID and version number.
    '''

    cursor = conn.cursor()

    try:
        # Retrieve the record ID
        cursor.execute('''
            SELECT id FROM form_definition.component_versions
            WHERE component_id = %s AND version_number = %s;
        ''', (component_id, version_number))

        record = cursor.fetchone()

        if record is None:
            raise Exception(f"Component version not found for component_id={component_id} and version_number={version_number}")

        return record['id']

    # If an exception occurs
    except Exception as e:
        raise Exception(f"Error retrieving record ID: {str(e)}")
    
    finally:
        cursor.close()  
        

# Method to obtain a component version
def get_component_version_from_db(component_id: int, version_number: int):
    '''
    Retrieve a component version from the database by component ID and version number.
    '''

    logger.info(f"Retrieving component version for component_id={component_id} and version_number={version_number}")

    # Get the connection to the database
    conn = get_connection()

    # Create a cursor
    cursor = conn.cursor()

    try:
        logger.debug(f"Executing query to retrieve component version for component_id={component_id} and version_number={version_number}")
        # Retrieve the component version
        cursor.execute('''
            SELECT id, component_id, version_number, definition,
                   default_props, validation_config, service_bindings, is_active, created_at, updated_at
            FROM form_definition.component_versions
            WHERE component_id = %s AND version_number = %s;
        ''', (component_id, version_number))

        component_version = cursor.fetchone()

        if component_version is None:
            logger.error(f"Component version not found for component_id={component_id} and version_number={version_number}")
            raise Exception(f"Component version not found for component_id={component_id} and version_number={version_number}")

        # Return the component version details
        return component_version

    # If an exception occurs
    except Exception as e:
        logger.error(f"Error retrieving component version for component_id={component_id} and version_number={version_number}: {str(e)}", exc_info=True)    
        # Raise an exception to be handled by the caller
        raise Exception(f"Error retrieving component version: {str(e)}")
    
    finally:
        # Close the cursor and connection
        cursor.close()
        close_connection()


# Method to obtain the latest version of a component
def get_latest_component_version_from_db(component_id: int):
    '''
    Retrieve the latest component version from the database by component ID.
    '''

    logger.info(f"Retrieving latest component version for component_id={component_id}")

    # Get the connection to the database
    conn = get_connection()

    # Create a cursor
    cursor = conn.cursor()

    try:
        logger.debug(f"Executing query to retrieve latest component version for component_id={component_id}")
        # Retrieve the latest component version
        cursor.execute('''
            SELECT id, component_id, version_number, definition,
                   default_props, validation_config, service_bindings, is_active, created_at, updated_at
            FROM form_definition.component_versions
            WHERE component_id = %s
            ORDER BY version_number DESC
            LIMIT 1;
        ''', (component_id,))

        component_version = cursor.fetchone()

        if component_version is None:
            logger.error(f"No component versions found for component_id={component_id}")
            raise Exception(f"No component versions found for component_id={component_id}")

        # Return the latest component version details
        return component_version

    # If an exception occurs
    except Exception as e:
        logger.error(f"Error retrieving latest component version for component_id={component_id}: {str(e)}", exc_info=True)    
        # Raise an exception to be handled by the caller
        raise Exception(f"Error retrieving latest component version: {str(e)}")
    
    finally:
        # Close the cursor and connection
        cursor.close()
        close_connection()


# Method to obtain all versions of a component
def get_all_versions_from_db(component_id: int):
    '''
    Retrieve all versions for the component
    '''

    logger.info(f"Retrieving all component versions for component_id={component_id}")

    # Get the connection to the database
    conn = get_connection()

    # Create a cursor
    cursor = conn.cursor()

    try:
        logger.debug(f"Executing query to retrieve latest component version for component_id={component_id}")

        # Execute query
        cursor.execute('''
            SELECT id, component_id, version_number, definition,
                   default_props, validation_config, service_bindings, is_active, created_at, updated_at
            FROM form_definition.component_versions
            WHERE component_id = %s
            ORDER BY version_number DESC
        ''', (component_id,))

        # Get all versions
        components = cursor.fetchall()

        # Check if the list is empty and raise exception
        if components is None:
            logger.error(f"No component versions found for component_id={component_id}")
            raise Exception(f"No component versions found for component_id={component_id}")

        # Return the version list
        return components

    except Exception as e:
        logger.error(f"Error retrieving the version list for component {component_id}: {str(e)}")
        raise Exception(f"Error retrieving version list: {str(e)}")
    
    finally:
        cursor.close()
        close_connection()


# Method to delete a specific version of a component
def delete_component_version_from_db(component_id: int, version_id: int):
    '''
    Delete a particular component version. Physical delete (row is eliminated)
    '''

    logger.info(f"Deleting from database component version {version_id} for component_id={component_id}")

    # Get the connection to the database
    conn = get_connection()

    # Create a cursor
    cursor = conn.cursor()

    try:
        logger.info(f"Executing DELETE for version {version_id} of compoent with id {component_id}")

        # Delete row
        cursor.execute('''
            DELETE FROM form_definition.component_versions 
            WHERE component_id = %s 
            AND version_number = %s;
        ''', (component_id, version_id))

        # Obtain info of deleted row
        deleted_row = cursor.fetchone()

        # If nothing was deleted, log a warning and raise exception
        if not deleted_row:
            logger.warning(f"No record found for version {version_id} for component with id {component_id}")
            raise Exception(f"Version {version_id} not found for component with ID {component_id}.")
            

        # Log success (only happens if deletion worked)
        logger.info(f"Successfully deleted version {version_id} of component with id {component_id}")

        # Commit changes
        conn.commit()

        # Return message
        return {"status": "Version successfully deleted", 
                "message": f"Version {version_id} for component {component_id} deleted."}

    except Exception as e:
        logger.error(f"Failed to delete version {version_id} of component with id {component_id}")
        raise Exception(f"Error deleting component version: {str(e)}")
    
    finally:
        cursor.close()
        close_connection()


# Method to delete the latest version of a component
def delete_lastest_version_from_db(component_id: int):
    '''
    Delete the latest version of the component.

    Uses the generic method delete_component_version_from_db which takes a component and
    a version number. First, it retrieves the right version. If no version is found, raises exception.
    '''

    # Find latest version
    version = get_latest_component_version_from_db(component_id)

    if not version:
        logger.warning(f"No version was found for component id {component_id}")
        raise Exception(f"No version found for component id {component_id}")
    
    # Obtain the version number
    version_number = version['version_number']
    logger.info(f"Latest component version is {version_number}... attempting to delete.")

    # Call detele method that is already generic for any version
    return delete_component_version_from_db(component_id, version_number)