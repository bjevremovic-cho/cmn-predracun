# -*- coding: utf-8 -*-
import os

DATABASE_URL = os.environ.get('DATABASE_URL', '')

def get_db():
    if DATABASE_URL:
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect(DATABASE_URL)
        return conn, 'pg'
    else:
        import sqlite3
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'cmn.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn, 'sqlite'

def q(sql, args=(), one=False, commit=False):
    conn, db_type = get_db()
    try:
        if db_type == 'pg':
            import psycopg2.extras
            # Convert ? to %s for PostgreSQL
            pg_sql = sql.replace('?', '%s')
            # Add RETURNING id for INSERT if commit
            if commit and pg_sql.strip().upper().startswith('INSERT') and 'RETURNING' not in pg_sql.upper():
                pg_sql += ' RETURNING id'
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(pg_sql, args if args else None)
            conn.commit()
            if commit:
                try:
                    row = cur.fetchone()
                    conn.close()
                    return row['id'] if row and 'id' in row else None
                except:
                    conn.close()
                    return None
            rv = cur.fetchone() if one else cur.fetchall()
            conn.close()
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
        except:
            pass
        raise e
