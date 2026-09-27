import sqlite3
import string
import random
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

app = FastAPI()

# Database connection setup
conn = sqlite3.connect("urls.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS urls (short_code TEXT PRIMARY KEY, original_url TEXT)")
conn.commit()

# Input data model validation
class URLRequest(BaseModel):
    url: str

# Function to generate a random 6-character short code
def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# ENDPOINT 1: Convert long URL into a short code
@app.post("/shorten")
def shorten_url(request: URLRequest):
    short_code = generate_short_code()
    cursor.execute("INSERT INTO urls (short_code, original_url) VALUES (?, ?)", (short_code, request.url))
    conn.commit()
    return {"short_code": short_code, "short_url": f"http://127.0.0.1:8000/{short_code}"}

# ENDPOINT 2: Total count of URLs in database
@app.get("/stats/count")
def get_total_urls():
    cursor.execute("SELECT COUNT(*) FROM urls")
    count = cursor.fetchone()[0]
    return {"total_shortened_urls": count}

# ENDPOINT 3: Redirect short code to original URL
@app.get("/{short_code}")
def redirect_to_url(short_code: str):
    cursor.execute("SELECT original_url FROM urls WHERE short_code = ?", (short_code,))
    result = cursor.fetchone()
    if result:
        return RedirectResponse(url=result[0])
    raise HTTPException(status_code=404, detail="URL not found")

