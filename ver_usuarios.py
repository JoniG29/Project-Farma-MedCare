# show_users.py

# 1. Importa los componentes necesarios de tu app.py
# Nota: Asegúrate de que este script esté en el mismo nivel que app.py
from app import app, db, User

# 2. Inicia el contexto de la aplicación para que SQLAlchemy funcione
with app.app_context():
    # 3. Consulta a todos los usuarios
    usuarios = User.query.all()

    # 4. Verifica si hay usuarios
    if not usuarios:
        print("\n--- NO SE ENCONTRARON USUARIOS REGISTRADOS ---")
    else:
        print("\n--- DETALLE DE USUARIOS Y HASHES DE CONTRASEÑA ---")

        # 5. Itera e imprime la información de cada usuario
        for u in usuarios:
            print("-------------------------------------------------")
            print(f"ID: {u.id}")
            print(f"Username: {u.username}")
            print(f"Nombre Completo: {u.full_name}")
            print(f"Email: {u.email}")

            # ** CAMPO FALTANTE AÑADIDO **
            print(f"Dirección: {u.address or 'N/A'}")

            print(f"Teléfono: {u.phone_number or 'N/A'}")

            # ** COLUMNA DE CONTRASEÑA CORREGIDA **
            # La columna donde se guarda el hash de la contraseña ahora se llama 'password'
            print(f"HASH (password): {u.password_hash}")

        print("-------------------------------------------------")