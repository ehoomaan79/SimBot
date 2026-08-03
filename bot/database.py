import sqlite3


DB = "players.db"


def connect():
    return sqlite3.connect(DB)



def init_db():

    conn = connect()
    cur = conn.cursor()


    cur.execute("""
    CREATE TABLE IF NOT EXISTS players
    (
        fid TEXT PRIMARY KEY,
        kid TEXT,
        discord_id TEXT
    )
    """)


    cur.execute("""
    CREATE TABLE IF NOT EXISTS gift_codes
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        active INTEGER DEFAULT 1,
        created_at INTEGER
    )
    """)


    conn.commit()
    conn.close()



# ----------------------
# Gift code functions
# ----------------------

def add_code(code):

    import time

    conn = connect()
    cur = conn.cursor()


    try:

        cur.execute("""
        INSERT INTO gift_codes
        (
            code,
            created_at
        )
        VALUES (?,?)
        """,
        (
            code,
            int(time.time())
        ))

        conn.commit()

        return True


    except sqlite3.IntegrityError:

        return False


    finally:

        conn.close()



def get_latest_code():

    conn = connect()
    cur = conn.cursor()


    cur.execute("""
    SELECT code
    FROM gift_codes
    WHERE active=1
    ORDER BY id DESC
    LIMIT 1
    """)


    result = cur.fetchone()

    conn.close()


    if result:
        return result[0]

    return None



def remove_code(code):

    conn = connect()
    cur = conn.cursor()


    cur.execute("""
    UPDATE gift_codes
    SET active=0
    WHERE code=?
    """,
    (code,))


    conn.commit()
    conn.close()
def add_player(fid, kid, discord_id):

    conn = sqlite3.connect(DB)

    cur = conn.cursor()

    cur.execute("""
    INSERT OR IGNORE INTO players
    (
        fid,
        kid,
        discord_id
    )
    VALUES (?, ?, ?)
    """,
    (
        fid,
        kid,
        discord_id
    ))

    conn.commit()
    conn.close()



def player_exists(fid):

    conn = sqlite3.connect(DB)

    cur = conn.cursor()

    cur.execute(
        "SELECT fid FROM players WHERE fid=?",
        (fid,)
    )

    result = cur.fetchone()

    conn.close()

    return result is not None