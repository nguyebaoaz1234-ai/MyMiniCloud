from flask import Flask, jsonify, request, render_template_string
import requests, os, json
import pymysql
from jose import jwt

app = Flask(__name__)

# Cấu hình Database MariaDB
DB_HOST = os.getenv("DB_HOST", "relational-database-server")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "root")
DB_NAME = os.getenv("DB_NAME", "studentdb")

# Cấu hình Keycloak OIDC
KEYCLOAK_INTERNAL_URL = os.getenv("KEYCLOAK_INTERNAL_URL", "http://authentication-identity-server:8080")
DEFAULT_REALM = os.getenv("OIDC_REALM", "realm_52400003")

# Giao diện bảng HTML màu tím giống hệt hình mẫu trong đề bài
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f8f9fa;
            margin: 40px auto;
            max-width: 900px;
            padding: 0 20px;
        }
        h2 {
            color: #4f46e5;
            font-size: 22px;
            margin-bottom: 16px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: #ffffff;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }
        th {
            background-color: #4f46e5;
            color: #ffffff;
            text-align: left;
            padding: 14px 18px;
            font-size: 14px;
        }
        td {
            padding: 14px 18px;
            border-bottom: 1px solid #f1f5f9;
            font-size: 14px;
            color: #1e293b;
        }
        tr:last-child td {
            border-bottom: none;
        }
    </style>
</head>
<body>
    <h2>{{ title }}</h2>
    <table>
        <thead>
            <tr>
                {% for h in headers %}
                <th>{{ h }}</th>
                {% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for row in rows %}
            <tr>
                {% for cell in row %}
                <td>{{ cell }}</td>
                {% endfor %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

def wants_html():
    # Nếu mở trên trình duyệt (Chrome/Edge) thì hiển thị bảng HTML, nếu dùng curl thì trả về JSON
    accept = request.headers.get("Accept", "")
    return "text/html" in accept and "curl" not in request.headers.get("User-Agent", "").lower()

def get_jwks(realm_name):
    jwks_url = f"{KEYCLOAK_INTERNAL_URL}/realms/{realm_name}/protocol/openid-connect/certs"
    return requests.get(jwks_url, timeout=5).json()

@app.get("/hello")
def hello():
    return jsonify(message="Hello from App Server!")

# Mở rộng 2 & 9: API /student đọc từ file students.json
@app.get("/student")
def student():
    with open("students.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    if wants_html():
        rows = [[s.get("id"), s.get("name"), s.get("major"), s.get("gpa")] for s in data]
        return render_template_string(
            HTML_TEMPLATE,
            title="Danh sách sinh viên (JSON)",
            headers=["ID", "Name", "Major", "GPA"],
            rows=rows
        )
    return jsonify(data)

# Mở rộng 3: API /students-db đọc trực tiếp từ bảng students trong MariaDB
@app.get("/students-db")
def students_db():
    try:
        conn = pymysql.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, student_id, fullname, CAST(dob AS CHAR) AS dob, major FROM students;")
            data = cursor.fetchall()
        conn.close()
        if wants_html():
            rows = [[s.get("id"), s.get("student_id"), s.get("fullname"), s.get("dob"), s.get("major")] for s in data]
            return render_template_string(
                HTML_TEMPLATE,
                title="Danh sách sinh viên (MariaDB)",
                headers=["#", "Student ID", "Fullname", "DOB", "Major"],
                rows=rows
            )
        return jsonify(data)
    except Exception as e:
        return jsonify(error=str(e)), 500

# Cơ bản & Mở rộng 4: API /secure xác thực OIDC Access Token từ Keycloak
@app.get("/secure")
def secure():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify(error="Missing Bearer token"), 401
    token = auth.split(" ", 1)[1].strip()
    try:
        unverified = jwt.get_unverified_claims(token)
        iss = unverified.get("iss", "")
        realm_name = iss.split("/realms/")[-1] if "/realms/" in iss else DEFAULT_REALM

        jwks = get_jwks(realm_name)
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            options={"verify_aud": False, "verify_iss": False}
        )
        return jsonify(
            message="Secure resource OK",
            realm=realm_name,
            client_id=payload.get("azp"),
            preferred_username=payload.get("preferred_username")
        )
    except Exception as e:
        return jsonify(error=str(e)), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)