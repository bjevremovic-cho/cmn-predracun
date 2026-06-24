# -*- coding: utf-8 -*-
"""
Database abstraction layer.
Uses PostgreSQL (via DATABASE_URL env var) or SQLite as fallback.
"""
import os
import sqlite3

DATABASE_URL = os.environ.get('DATABASE_URL', '')

def get_db():
    if DATABASE_URL:
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        return conn, 'pg'
    else:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'cmn.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn, 'sqlite'

def q(sql, args=(), one=False, commit=False):
    """Execute SQL, return results. Handles both PG and SQLite."""
    conn, db_type = get_db()
    try:
        if db_type == 'pg':
            import psycopg2.extras
            # Convert SQLite ? placeholders to PostgreSQL %s
            pg_sql = sql.replace('?', '%s')
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(pg_sql, args if args else None)
            if commit:
                conn.commit()
                lid = cur.fetchone()
                conn.close()
                return lid['id'] if lid and 'id' in lid else None
            rv = cur.fetchone() if one else cur.fetchall()
            conn.close()
            # Convert to list of dicts
            if rv is None:
                return None if one else []
            if one:
                return dict(rv)
            return [dict(r) for r in rv]
        else:
            cur = conn.execute(sql, args)
            if commit:
                conn.commit()
                lid = cur.lastrowid
                conn.close()
                return lid
            rv = cur.fetchone() if one else cur.fetchall()
            conn.close()
            return rv
    except Exception as e:
        try:
            conn.rollback()
            conn.close()
        except: pass
        raise e
