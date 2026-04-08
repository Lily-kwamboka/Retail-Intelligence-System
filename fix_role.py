from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv('DB_URL'))
with engine.begin() as conn:
    conn.execute(text("""
        UPDATE users SET role = 'admin' WHERE email = 'bernicewakarindi@gmail.com'
    """))
print('Role updated to admin!')