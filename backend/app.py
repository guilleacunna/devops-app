import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, request

app = Flask(__name__)

# Configuración de conexión a PostgreSQL
DB_HOST = os.getenv('DB_HOST', 'postgres_db')
DB_NAME = os.getenv('DB_NAME', 'devdb')
DB_USER = os.getenv('DB_USER', 'devuser')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'devpassword')

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor  # Retorna las filas como diccionarios/JSON
    )
    return conn

def init_db():
    """Crea la tabla 'usuarios' si aún no existe en la base de datos."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Tabla 'usuarios' verificada/creada correctamente.")
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")

# Ejecutar la creación de la tabla al arrancar la app
init_db()

@app.route('/')
def health_check():
    return jsonify({
        "status": "online",
        "message": "API de Flask ejecutándose correctamente"
    }), 200

# 📍 Endpoint 1: Obtener todos los usuarios
@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, nombre, email, fecha_creacion FROM usuarios ORDER BY id ASC;')
        usuarios = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(usuarios), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 📍 Endpoint 2: Crear un nuevo usuario
@app.route('/usuarios', methods=['POST'])
def create_usuario():
    data = request.get_json()
    if not data or 'nombre' not in data or 'email' not in data:
        return jsonify({"error": "Faltan los campos requeridos: nombre y email"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO usuarios (nombre, email) VALUES (%s, %s) RETURNING id, nombre, email, fecha_creacion;',
            (data['nombre'], data['email'])
        )
        nuevo_usuario = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(nuevo_usuario), 201
    except Exception as e:
        return jsonify({"error": f"Error al guardar en la base de datos: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)