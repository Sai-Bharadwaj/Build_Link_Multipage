from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory


BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "buildlink.db"

app = Flask(__name__, static_folder=None)


def get_db() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_db() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page TEXT NOT NULL,
                form_type TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                category TEXT,
                location TEXT,
                description TEXT,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS contractors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                location TEXT,
                contact TEXT,
                experience TEXT,
                capabilities TEXT,
                created_at TEXT NOT NULL
            );
            """
        )


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def clean_payload(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {str(key): str(item).strip() for key, item in value.items() if item is not None}


@app.get("/api/health")
def health() -> tuple[dict, int]:
    return {"status": "ok", "database": str(DATABASE.name)}, 200


@app.post("/api/submissions")
def create_submission():
    body = request.get_json(silent=True) or {}
    page = str(body.get("page", "unknown")).strip() or "unknown"
    form_type = str(body.get("form_type", "form")).strip() or "form"
    payload = clean_payload(body.get("data"))
    if not payload:
        return jsonify({"error": "Please complete at least one field."}), 400

    created_at = now()
    with get_db() as connection:
        cursor = connection.execute(
            "INSERT INTO submissions (page, form_type, payload, created_at) VALUES (?, ?, ?, ?)",
            (page, form_type, json.dumps(payload), created_at),
        )

        if form_type == "project":
            connection.execute(
                "INSERT INTO projects (title, company, category, location, description, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    payload.get("Project title", "Untitled project"),
                    payload.get("Company name", "Unknown company"),
                    payload.get("Select category", ""),
                    payload.get("Project location", ""),
                    payload.get("Describe scope, capability needed and timeline", ""),
                    created_at,
                ),
            )
        elif form_type == "contractor":
            connection.execute(
                "INSERT INTO contractors (name, category, location, contact, experience, capabilities, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    payload.get("Business / contractor name", "Unnamed contractor"),
                    payload.get("Trade / category", ""),
                    payload.get("Service location", ""),
                    payload.get("Primary contact", ""),
                    payload.get("Years of experience", ""),
                    payload.get("Capabilities and past project experience", ""),
                    created_at,
                ),
            )

    return jsonify({"id": cursor.lastrowid, "message": "Saved successfully."}), 201


@app.get("/api/search")
def search_contractors():
    category = request.args.get("category", "").strip()
    location = request.args.get("location", "").strip()
    search_payload = {"category": category, "location": location}
    with get_db() as connection:
        connection.execute(
            "INSERT INTO submissions (page, form_type, payload, created_at) VALUES (?, ?, ?, ?)",
            ("/find-contractors.html", "contractor-search", json.dumps(search_payload), now()),
        )
    query = "SELECT * FROM contractors WHERE 1 = 1"
    values: list[str] = []
    if category and not category.lower().startswith("select"):
        query += " AND category LIKE ?"
        values.append(f"%{category}%")
    if location:
        query += " AND location LIKE ?"
        values.append(f"%{location}%")
    query += " ORDER BY created_at DESC"
    with get_db() as connection:
        results = [dict(row) for row in connection.execute(query, values).fetchall()]
    return jsonify({"results": results, "count": len(results)})


@app.get("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.get("/<path:filename>")
def website_file(filename: str):
    requested = BASE_DIR / filename
    if requested.is_file() and BASE_DIR in requested.resolve().parents:
        return send_from_directory(BASE_DIR, filename)
    return send_from_directory(BASE_DIR, "index.html")


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)
else:
    init_db()
