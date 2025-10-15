from db_handler import get_connection, close_connection
from fastapi import HTTPException
from models.component_models import Component
import json

def create_component(component: Component):
    """
    Handle creation of new component in the database.

    Takes a Component object as input and inserts it into the database.
    Returns the newly created component details.
    """

    # Get the connection to the database
    conn = get_connection()

    # Create a cursor
    cursor = conn.cursor()

    try:
        # Insert the new component into the database
        cursor.execute('''
            INSERT INTO form_definition.components (key, name, description, base_component_id, category, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, now(), now())
            RETURNING id, key, name, description, base_component_id, category, created_at, updated_at;
        ''', (component.key,
              component.name,
              component.description,
              getattr(component, "base_component_id", None),
              component.category
              ))

        # Fetch the newly created component
        new_component = cursor.fetchone()

        # Commit the transaction
        conn.commit()

        # Return the new component details
        return new_component

    # If an exception occurs
    except Exception as e:
        # Rollback the transaction in case of error
        conn.rollback()

        # Raise the exception to be handled by the caller
        raise Exception(f"Error creating component: {str(e)}")
    
    finally:
        # Close the cursor and connection
        cursor.close()
        close_connection()


def update_component(component_id: int, component: Component):
    """
    Handle updating an existing component in the database.

    Takes a component ID and a Component object as input.
    Updates the corresponding component in the database.
    Returns the updated component details.
    """

    # Get the connection to the database
    conn = get_connection()

    # Create a cursor
    cursor = conn.cursor()

    try:
        # Update the existing component in the database
        cursor.execute('''
            UPDATE form_definition.components
            SET key = %s,
                name = %s,
                description = %s,
                updated_at = now()
            WHERE id = %s
            RETURNING id, key, name, description, created_at, updated_at;
        ''', (component.key, component.name, component.description, component_id))

        # Fetch the updated component
        updated_component = cursor.fetchone()

        if not updated_component:
            raise Exception(f"Component with ID {component_id} not found.")

        # Commit the transaction
        conn.commit()

        # Return the updated component details
        return updated_component

    # If an exception occurs
    except Exception as e:
        # Rollback the transaction in case of error
        conn.rollback()

        # Raise the exception to be handled by the caller
        raise Exception(f"Error updating component: {str(e)}")
    
    finally:
        # Close the cursor and connection
        cursor.close()
        close_connection()


def get_component_by_id(component_id: int):
    """
    Retrieve a component from the database by its ID.

    Takes a component ID as input and fetches the corresponding component from the database.
    Returns the component details if found, otherwise raises an exception.
    """

    # Get the connection to the database
    conn = get_connection()

    # Create a cursor
    cursor = conn.cursor()

    try:
        # Query to fetch the component by ID
        cursor.execute('''
            SELECT id, key, name, description, base_component_id, category, created_at, updated_at
            FROM form_definition.components
            WHERE id = %s;
        ''', (component_id,))

        # Fetch the component
        component = cursor.fetchone()

        if not component:
            raise Exception(f"Component with ID {component_id} not found.")

        # Return the component details
        return component

    # If an exception occurs
    except Exception as e:
        # Raise the exception to be handled by the caller
        raise Exception(f"Error retrieving component: {str(e)}")
    
    finally:
        # Close the cursor and connection
        cursor.close()
        close_connection()