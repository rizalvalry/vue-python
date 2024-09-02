from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import jwt
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import logging

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)

# Basic Auth
security = HTTPBasic()

# FastAPI Application
app = FastAPI(title="Changes Log API")

# listen port IP
origins = [
           "10.10.4.12:5001",
           "127.0.0.1:5001",
           "http://10.10.4.12:5001",
           "http://127.0.0.1:5001",
           "http://127.0.0.1:8080",
           "http://localhost:5001",
           "http://localhost:8080",
           "localhost:5001",
           ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fungsi verifikasi kredensial
def verify_credentials(credentials: HTTPBasicCredentials):
    correct_username = "LSadmin"
    correct_password = "password"
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# mendapatkan daftar tabel yang sesuai dengan pola nama tabel schema
def get_table_names(conn, table_prefix):
    with conn.cursor() as cursor:
        query = f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'changes_log' AND table_name LIKE '%{table_prefix}%'
        """
        cursor.execute(query)
        table_names = [row[0] for row in cursor.fetchall()]

    # Tambahkan logging untuk tabel yang ditemukan
    logging.info(f"Found tables: {table_names}")
    
    return table_names


# search union di semua tabel
def search_across_all_tables(
    conn,
    corporation: Optional[str] = None,
    primary_1_value: Optional[str] = None,
    primary_2_value: Optional[str] = None,
    primary_3_value: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    table_patterns = [corporation]  # corporation sebagai daftar pola
    table_names = []
    for pattern in table_patterns:
        table_names.extend(get_table_names(conn, pattern))
    
    if not table_names:
        logging.error("No tables found matching the pattern.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tables found matching the pattern."
        )

    base_query = f"SELECT * FROM changes_log.\"{{table_name}}\""

    where_clauses = []
    if primary_1_value:
        where_clauses.append(f"\"primaryKeyField1Value\" = '{primary_1_value}'")
    if primary_2_value:
        where_clauses.append(f"\"primaryKeyField2Value\" = '{primary_2_value}'")
    if primary_3_value:
        where_clauses.append(f"\"primaryKeyField3Value\" = '{primary_3_value}'")

    where_clause = " AND ".join(where_clauses)
    if where_clause:
        where_clause = " WHERE " + where_clause

    union_query = " UNION ALL ".join(
        [base_query.format(table_name=table) + where_clause for table in table_names]
    )
    
    # Menambahkan LIMIT dan OFFSET di sini
    union_query_with_limit = f"{union_query} LIMIT {limit} OFFSET {offset}"
    
    logging.info(f"Generated Query: {union_query_with_limit}")

    if not union_query_with_limit.strip():
        logging.error("Generated an empty query.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Generated an empty query."
        )

    return union_query_with_limit



# Endpoint login
@app.post("/token")
async def login(credentials: HTTPBasicCredentials = Depends(security)):
    username = verify_credentials(credentials)
    return {"message": f"Welcome, {username}!"}

# Default DB Config
DEFAULT_DB_CONFIG = {
    "host": "pgm-d9j1180a0905w1e04o.pgsql.ap-southeast-5.rds.aliyuncs.com",
    "database": "lscentral_log",
    "user": "mrizal",
    "password": "$%PntPr1!@#",
    "port": 1500
}

# Function to create a new database connection dynamically
def create_connection(db_config):
    try:
        conn = psycopg2.connect(**db_config)
        return conn
    except Exception as e:
        print(f"Error creating connection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database"
        )


@app.get("/refresh_data")
async def refresh_data(
    credentials: HTTPBasicCredentials = Depends(security)
):
    verify_credentials(credentials)
    
    # Buat koneksi ke DB
    conn = create_connection(DEFAULT_DB_CONFIG)

    # Refresh materialized views
    result = refresh_materialized_views(conn)
    
    # Tutup koneksi ke DB
    conn.close()
    
    return {"status": "success", "message": result}



# Function to refresh materialized views
def refresh_materialized_views(conn):
    try:
        with conn.cursor() as cursor:
            # Menjalankan perintah REFRESH MATERIALIZED VIEW
            cursor.execute("REFRESH MATERIALIZED VIEW changes_log.mv_top_users_pnt")
            cursor.execute("REFRESH MATERIALIZED VIEW changes_log.mv_top_users_pri")
            cursor.execute("REFRESH MATERIALIZED VIEW changes_log.mv_max_pnt")
            cursor.execute("REFRESH MATERIALIZED VIEW changes_log.mv_max_pri")
            conn.commit()

            logging.info("Successfully refreshed materialized views.")
            return "Materialized views refreshed successfully"
    except Exception as e:
        logging.error(f"Error refreshing materialized views: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh materialized views"
        )


@app.get("/global_search")
async def global_search(
    corporation: Optional[str] = Query(None),
    primary_1_value: Optional[str] = Query(None),
    primary_2_value: Optional[str] = Query(None),
    primary_3_value: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
    credentials: HTTPBasicCredentials = Depends(security)
):
    # Verifikasi kredensial
    verify_credentials(credentials)
    
    # Buat koneksi ke DB
    conn = create_connection(DEFAULT_DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        offset = (page - 1) * page_size

        # Buat query dengan pagination
        query = search_across_all_tables(
            conn=conn,
            corporation=corporation,
            primary_1_value=primary_1_value,
            primary_2_value=primary_2_value,
            primary_3_value=primary_3_value,
            limit=page_size,  # Kirim page_size sebagai limit
            offset=offset    # Kirim offset
        )
        
        cursor.execute(query)
        data = cursor.fetchall()

        # Return the paginated data
        return {
            "page": page,
            "page_size": page_size,
            "data": data
        }

    except psycopg2.Error as e:
        print(f"Error fetching data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching data"
        )
    finally:
        cursor.close()
        conn.close()


# views Materialize
@app.get("/materialized_views_data")
async def get_materialized_views_data(
    credentials: HTTPBasicCredentials = Depends(security)
):
    # Verifikasi kredensial
    verify_credentials(credentials)
    
    # Buat koneksi ke DB
    conn = create_connection(DEFAULT_DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute("SELECT * FROM changes_log.mv_top_users_pnt")
        result_pnt = cursor.fetchall()
        
        cursor.execute("SELECT * FROM changes_log.mv_top_users_pri")
        result_pri = cursor.fetchall()
        
        cursor.execute("SELECT * FROM changes_log.mv_max_pnt")
        result_max_pnt = cursor.fetchall()
        
        cursor.execute("SELECT * FROM changes_log.mv_max_pri")
        result_max_pri = cursor.fetchall()
        
        # Format data untuk response
        return {
            "top_users_pnt": result_pnt,
            "top_users_pri": result_pri,
            "max_pnt": result_max_pnt,
            "max_pri": result_max_pri
        }

    except psycopg2.Error as e:
        logging.error(f"Error fetching data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching data"
        )
    finally:
        cursor.close()
        conn.close()

 


# Endpoint size count rows & Endpoint users TOP 5
@app.get("/usage_all/{table_name}")
async def get_table_data(
    table_name: str,
    credentials: HTTPBasicCredentials = Depends(security)
):
    # Verify credentials
    verify_credentials(credentials)
    
    # Create a DB connection
    conn = create_connection(DEFAULT_DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:

        # Query pertama top 5 user berdasarkan penggunaan
        query1 = f"""
        SELECT count(*) as baris_penggunaan, "userID" 
        FROM changes_log."{table_name}" 
        GROUP BY "userID" 
        ORDER BY "baris_penggunaan" DESC 
        LIMIT 5;
        """

        # Query kedua entryNo tertinggi
        query2 = f"""
        SELECT "dateAndTime", "entryNo" 
        FROM changes_log."{table_name}" 
        WHERE "entryNo" = (SELECT MAX("entryNo") 
                           FROM changes_log."{table_name}");
        """

        # Eksekusi query 1
        cursor.execute(query1)
        data_result = cursor.fetchall()

        # Eksekusi query 2
        cursor.execute(query2)
        rows_count_data_result = cursor.fetchone()

        # hasil query format JSON
        result = {
            "data": [{"baris_penggunaan": row["baris_penggunaan"], "userID": row["userID"]} for row in data_result],
            "rowsCountData": [{"dateAndTime": rows_count_data_result["dateAndTime"], "entryNo": rows_count_data_result["entryNo"]}]
        }

        return result

    except psycopg2.Error as e:
        print(f"Error fetching data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching data"
        )
    finally:
        cursor.close()
        conn.close()

# Endpoint changeslog with pagination
@app.get("/changes_log/{table_name}")
async def get_table_data(
    table_name: str,
    credentials: HTTPBasicCredentials = Depends(security),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
    start_date: str = Query(None),
    end_date: str = Query(None),
    field_caption: Optional[str] = Query(None),
    table_caption: Optional[str] = Query(None),
    old_value: Optional[str] = Query(None),
    new_value: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None)
):
    # Verify credentials
    verify_credentials(credentials)
    
    # Create a DB connection
    conn = create_connection(DEFAULT_DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        offset = (page - 1) * page_size
        where_clauses = []

        if start_date and end_date:
            where_clauses.append(
                f"\"dateAndTime\" BETWEEN CAST('{start_date} 00:00:00' AS timestamp) AND CAST('{end_date} 23:59:59' AS timestamp)"
            )
        if field_caption:
            where_clauses.append(f"\"fieldCaption\" = '{field_caption}'")
        if table_caption:
            where_clauses.append(f"\"tableCaption\" = '{table_caption}'")
        if old_value:
            where_clauses.append(f"\"oldValue\" = '{old_value}'")
        if new_value:
            where_clauses.append(f"\"newValue\" = '{new_value}'")
        if user_id:
            where_clauses.append(f"\"userID\" = '{user_id}'")

        where_clause = " AND ".join(where_clauses)
        if where_clause:
            where_clause = "WHERE " + where_clause

        query = f"SELECT * FROM changes_log.\"{table_name}\" {where_clause} LIMIT {page_size} OFFSET {offset};"
        cursor.execute(query)
        data = cursor.fetchall()

        # Check if data is available
        if not data:
            if offset == 0:
                return {"page": page, "page_size": page_size, "data": data}
            else:
                raise HTTPException(status_code=404, detail="No data available for this page.")
        
        # Return the data
        return {
            "page": page,
            "page_size": page_size,
            "data": data
        }
    except psycopg2.Error as e:
        print(f"Error fetching data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching data"
        )
    finally:
        cursor.close()
        conn.close()

# Existing endpoints...

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5002)
