import psycopg2

from config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD
)


def get_connection():

    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (

            id SERIAL PRIMARY KEY,

            user_id VARCHAR(100),

            role VARCHAR(20),

            message TEXT,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()

    cursor.close()

    connection.close()


def save_message(
    user_id,
    role,
    message
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO conversations
        (user_id, role, message)

        VALUES (%s, %s, %s)
        """,

        (
            user_id,
            role,
            message
        )
    )

    connection.commit()

    cursor.close()

    connection.close()


def get_recent_messages(
    user_id,
    limit=10
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT role, message

        FROM conversations

        WHERE user_id = %s

        ORDER BY created_at DESC

        LIMIT %s
        """,

        (
            user_id,
            limit
        )
    )

    rows = cursor.fetchall()

    cursor.close()

    connection.close()

    rows.reverse()

    return rows