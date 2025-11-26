import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# --- 1. CONFIGURACIÓN ---
# Pega aquí tu URL de la base de datos (la EXTERNA que copiaste de Render)
DATABASE_URI = "postgresql://farmacia_db_n7h0_user:YGOv7BKHcIdVzjUe97DajD0XDjKwXyDw@dpg-d440f8uuk2gs739iorh0-a.oregon-postgres.render.com/farmacia_db_n7h0"

# ¡¡ IMPORTANTE !!
# Si tu URL empieza con "postgres://", cámbialo a "postgresql://"
if DATABASE_URI.startswith("postgres://"):
    DATABASE_URI = DATABASE_URI.replace("postgres://", "postgresql://", 1)

# --- 2. CONFIGURACIÓN DE LA APP ---
# Esto es necesario para que SQLAlchemy sepa con qué app trabajar
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
db = SQLAlchemy(app)


# --- 3. MODELO DE USUARIO ---
# Copia y pega tu modelo User EXACTAMENTE como está en app.py
# (Asegúrate de que password_hash tenga String(256))
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f"<User {self.id}: {self.username} ({self.email})>"


# --- 4. FUNCIÓN PARA MOSTRAR USUARIOS ---
def mostrar_usuarios():
    print("Conectando a la base de datos de Render...")
    try:
        # Usamos app_context() para que la conexión funcione
        with app.app_context():
            # Buscamos todos los usuarios en la base de datos
            usuarios = db.session.scalars(db.select(User)).all()

            if not usuarios:
                print(">>> No se encontraron usuarios en la base de datos.")
                return

            print("\n--- LISTA DE USUARIOS REGISTRADOS ---")
            for usuario in usuarios:
                print(f"ID: {usuario.id}")
                print(f"  Username: {usuario.username}")
                print(f"  Full Name: {usuario.full_name}")
                print(f"  Email: {usuario.email}")
                print(f"  Address: {usuario.address}")
                print("-" * 20)

            print(f"\n>>> Total de usuarios: {len(usuarios)}")

    except Exception as e:
        print(f"Error al conectar o consultar la base de datos:")
        print(f"\n{e}")


# --- 5. EJECUTAR LA FUNCIÓN ---
if __name__ == "__main__":
    mostrar_usuarios()