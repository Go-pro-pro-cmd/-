import sqlite3
import logging

def create_database():
    connection = sqlite3.connect('tg_to_max.db')
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        TG_id INT,
        MAX_id INT,
        name TEXT NOT NULL,
        first_name TEXT,
        last_name TEXT,
        child_name TEXT
    )
    """)

    cursor.execute("""
     CREATE TABLE IF NOT EXISTS messages(
    mTG_id TEXT,
    mMAX_id TEXT,
    sender_name NOT NULL
     )

""")

    connection.commit()
    connection.close()

# create_database()

def take_user_name(id, messanger):
    connection = sqlite3.connect('tg_to_max.db')
    cursor = connection.cursor()
     
    if(messanger == 'MAX'):
             cursor.execute("SELECT name FROM users WHERE MAX_id = ? ", (id,))
             res = cursor.fetchone()
     
    if(messanger == 'TG'):
                 cursor.execute("SELECT name FROM users WHERE TG_id = ? ", (id,))
                 res = cursor.fetchone()
     
     
    if res:
             return res[0]
    else:
             return False
     

# def take_user_id(id, messanger):
#     connection = sqlite3.connect('tg_to_max.db')
#     cursor = connection.cursor()

#     if(messanger == 'MAX'):
#         cursor.execute("SELECT name FROM users WHERE MAX_id = ? ", (id,))
#         res = cursor.fetchone()

#     if(messanger == 'TG'):
#             cursor.execute("SELECT name FROM users WHERE TG_id = ? ", (id,))
#             res = cursor.fetchone()


#     if res:
#         return res[0]
#     else:
#         return False

def create_message_pair(mTG_id, mMAX_id, name):
    # name = take_user_name(user_id, messanger)

    connection = sqlite3.connect('tg_to_max.db')
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO messages(mTG_id, mMAX_id, sender_name)
            VALUES (?, ?,?)

        """, (mTG_id, mMAX_id, name))
        
        connection.commit()
        connection.close()
        return True
    except Exception as er:
          logging.error(f"Ошибка. Функция create_message_pair. Комментарий: {er}")