import sqlite3

from logger import get_logger


logger = get_logger(__name__)
DB = "players.db"


def connect():
    return sqlite3.connect(DB)


def init_db():
    logger.info("Initializing database")

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
        created_at INTEGER,
        expires_at INTEGER
    )
    """)

    conn.commit()
    conn.close()
    logger.info("Database initialized")


# ----------------------
# Gift code functions
# ----------------------

def add_code(code, expires_at=None):
    import time

    conn = connect()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO gift_codes
            (
                code,
                created_at,
                expires_at
            )
            VALUES (?,?,?)
            """,
            (
                code,
                int(time.time()),
                int(expires_at) if expires_at else None,
            ),
        )

        conn.commit()
        logger.info("Added gift code %s (expires_at=%s)", code, expires_at)
        return True

    except sqlite3.IntegrityError:
        logger.warning("Gift code %s already exists", code)
        return False

    finally:
        conn.close()


def get_latest_code():
    import time

    now = int(time.time())

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT code
        FROM gift_codes
        WHERE active=1 AND (expires_at IS NULL OR expires_at>?)
        ORDER BY id DESC
        LIMIT 1
        """,
        (now,),
    )

    result = cur.fetchone()
    conn.close()

    if result:
        logger.debug("Selected active gift code %s", result[0])
        return result[0]

    logger.debug("No active gift code available")
    return None


def remove_code(code):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    UPDATE gift_codes
    SET active=0
    WHERE code=?
    """, (code,))

    removed = cur.rowcount
    conn.commit()
    conn.close()
    logger.info("Disabled gift code %s", code)
    return removed > 0


def get_active_codes():
    import time

    now = int(time.time())
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT code FROM gift_codes
        WHERE active=1 AND (expires_at IS NULL OR expires_at>?)
        ORDER BY id DESC
        """,
        (now,),
    )

    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    logger.debug("Found %s active gift codes", len(rows))
    return rows


def remove_expired_codes():
    import time

    now = int(time.time())
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE gift_codes
        SET active=0
        WHERE active=1 AND expires_at IS NOT NULL AND expires_at<=?
        """,
        (now,),
    )

    removed = cur.rowcount
    conn.commit()
    conn.close()
    logger.info("Removed %s expired gift codes", removed)


def get_all_players():
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT fid, kid FROM players")
    rows = cur.fetchall()
    conn.close()
    logger.debug("Loaded %s players from database", len(rows))
    return rows


def add_player(fid, kid, discord_id):
    conn = sqlite3.connect(DB)

    cur = conn.cursor()

    cur.execute(
        "SELECT fid FROM players WHERE fid=?",
        (fid,),
    )
    exists = cur.fetchone() is not None

    if exists:
        conn.close()
        logger.info("Player %s already exists", fid)
        return False

    cur.execute(
        """
        INSERT INTO players
        (
            fid,
            kid,
            discord_id
        )
        VALUES (?, ?, ?)
        """,
        (fid, kid, discord_id),
    )

    conn.commit()
    conn.close()
    logger.info("Registered player %s with kingdom %s", fid, kid)
    return True


def remove_player(fid):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("DELETE FROM players WHERE fid=?", (fid,))
    removed = cur.rowcount

    conn.commit()
    conn.close()
    logger.info("Removed player %s from database", fid)
    return removed > 0


def player_exists(fid):
    conn = sqlite3.connect(DB)

    cur = conn.cursor()

    cur.execute("SELECT fid FROM players WHERE fid=?", (fid,))

    result = cur.fetchone()

    conn.close()
    logger.debug("Checked whether player %s exists: %s", fid, result is not None)
    return result is not None