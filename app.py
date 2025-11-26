import os
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import re

# Inicialización de la aplicación Flask
app = Flask(__name__)

# --- CONFIGURACIÓN DE LA BASE DE DATOS Y SESIÓN ---
# Busca la URL de Render. Si no existe, usa SQLite local.
DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///farmacia.db')

# Corrección para PostgreSQL en Render
if DATABASE_URI.startswith("postgres://"):
    DATABASE_URI = DATABASE_URI.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

# Clave secreta desde variable de entorno o por defecto para local
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave_local_de_prueba')

db = SQLAlchemy(app)


# ----------------------------------------
# MODELO DE USUARIO
# ----------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # Aumentado a 256 para evitar errores de longitud
    password_hash = db.Column(db.String(256))

    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


with app.app_context():
    db.create_all()

# --- Paleta de colores y Datos Estáticos ---
COLOR_VERDE_MENTA = "#A1E8D5"
COLOR_AZUL_CIELO = "#87CEFA"
COLOR_GRIS_CALIDO = "#F0F0F0"
COLOR_BLANCO = "#FFFFFF"
COLOR_ROJO_CORAL = "#FF6347"
COLOR_AZUL_OSCURO = "#003366"

COLORES = {
    "verde_menta": COLOR_VERDE_MENTA,
    "azul_cielo": COLOR_AZUL_CIELO,
    "gris_calido": COLOR_GRIS_CALIDO,
    "blanco": COLOR_BLANCO,
    "rojo_coral": COLOR_ROJO_CORAL,
    "azul_oscuro": COLOR_AZUL_OSCURO
}

CATEGORIAS_MENU = ["Salud", "Bebés", "Vitaminas y Suplementos", "Ayuda"]

# --- BASE DE DATOS MAESTRA DE PRODUCTOS ---
PRODUCTOS_DB = {
    # Productos Destacados
    'p1': {"id": "p1", "nombre": "Analgésico", "precio": 99.00, "imagen_placeholder": "Analgesico"},
    'p2': {"id": "p2", "nombre": "Multivitamínico", "precio": 180.50, "imagen_placeholder": "Multivitaminico"},
    'p3': {"id": "p3", "nombre": "Protector Solar", "precio": 150.00, "imagen_placeholder": "ProtectorSolar"},
    'p4': {"id": "p4", "nombre": "Vitamina C", "precio": 120.00, "imagen_placeholder": "VitaminaC"},

    # Antibióticos
    'a1': {"id": "a1", "nombre": "Amoxicilina 500mg", "precio": 85.00, "imagen_placeholder": "Amoxicilina"},
    'a2': {"id": "a2", "nombre": "Azitromicina 250mg", "precio": 130.00, "imagen_placeholder": "Azitromicina"},
    'a3': {"id": "a3", "nombre": "Ciprofloxacino", "precio": 110.00, "imagen_placeholder": "Ciprofloxacino"},
    'a4': {"id": "a4", "nombre": "Metronidazol", "precio": 75.00, "imagen_placeholder": "Metronidazol"},
}

# Listas que solo contienen los IDs
PRODUCTOS_DESTACADOS_IDS = ['p1', 'p2', 'p3', 'p4']
ANTIBIOTICOS_DATA_IDS = ['a1', 'a2', 'a3', 'a4']

CATEGORIAS_EXTENDIDAS = [
    ("Cuidado de la Piel", "🧴", "Productos para el rostro y cuerpo."),
    ("Primeros Auxilios", "🩹", "Kits esenciales para emergencias."),
    ("Nutrición Deportiva", "💪", "Proteínas, barras y suplementos."),
    ("Medicina Natural", "🌿", "Opciones homeopáticas y herbolarias."),
    ("Salud Visual", "👁️", "Lentes de contacto y gotas."),
    ("Higiene Personal", "🧼", "Jabones, champús y desodorantes."),
]

BEBES_DATA = ["Fórmulas Infantiles", "Pañales", "Cuidado del Bebé", "Alimentos para Bebé"]
VITAMINAS_SUPLEMENTOS_DATA = ["Complementos Alimenticios", "Multivitaminas", "Suplementos Alimenticios"]
AYUDA_DATA = ["Contáctanos", "Preguntas Frecuentes", "Localizador de SuperFarmacias"]


# ----------------------------------------
# DECORADOR DE RESTRICCIÓN DE ACCESO
# ----------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash("Necesitas iniciar sesión para acceder a esta página.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


# ----------------------------------------
# GESTIÓN DE LA SESIÓN
# ----------------------------------------
@app.context_processor
def inject_user():
    return dict(logged_in=session.get('logged_in'), username=session.get('username'))


# ----------------------------------------
# RUTAS DE AUTENTICACIÓN
# ----------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        address = request.form.get('address')
        phone_number = request.form.get('phone_number')

        if not username or not password or not full_name or not email or not confirm_password:
            return render_template('register.html', error="Todos los campos con (*) son requeridos.", colores=COLORES)

        if password != confirm_password:
            return render_template('register.html', error="Error: Las contraseñas ingresadas no coinciden.",
                                   colores=COLORES)

        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Error: El nombre de usuario ya está registrado.",
                                   colores=COLORES)

        if User.query.filter_by(email=email).first():
            return render_template('register.html', error="Error: El email ya está registrado.", colores=COLORES)

        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
            error_msg = "La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula, un número y un símbolo (@$!%*?&)."
            return render_template('register.html', error=error_msg, colores=COLORES)

        new_user = User(
            username=username,
            full_name=full_name,
            email=email,
            address=address,
            phone_number=phone_number
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        session['logged_in'] = True
        session['username'] = username

        return redirect(url_for('home'))

    return render_template('register.html', colores=COLORES)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash("Usuario o contraseña incorrectos.", "error")
            return render_template('login.html', colores=COLORES)

    return render_template('login.html', colores=COLORES)


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        flash(
            "Si el correo electrónico está registrado, recibirás un enlace para restablecer tu contraseña. (Función simulada)",
            "info")
        return redirect(url_for('login'))
    return render_template('forgot_password.html', colores=COLORES)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('cart', None)  # Opcional: limpiar carrito al salir
    return redirect(url_for('login'))


# ----------------------------------------
# RUTAS DE NAVEGACIÓN PROTEGIDAS
# ----------------------------------------

@app.route('/')
@login_required
def home():
    # Convertimos los IDs en objetos completos
    productos_completos = [PRODUCTOS_DB[pid] for pid in PRODUCTOS_DESTACADOS_IDS if pid in PRODUCTOS_DB]

    return render_template(
        'index.html',
        categorias=CATEGORIAS_MENU,
        productos=productos_completos,
        categorias_extendidas=CATEGORIAS_EXTENDIDAS,
        colores=COLORES
    )


@app.route('/profile')
@login_required
def profile():
    return render_template(
        'profile.html',
        categorias=CATEGORIAS_MENU,
        colores=COLORES
    )


@app.route('/pagina/Antibioticos')
@login_required
def antibioticos_page():
    # Convertimos los IDs en objetos completos
    productos_completos = [PRODUCTOS_DB[pid] for pid in ANTIBIOTICOS_DATA_IDS if pid in PRODUCTOS_DB]

    return render_template(
        'antibioticos.html',
        categorias=CATEGORIAS_MENU,
        productos_antibioticos=productos_completos,
        colores=COLORES
    )


@app.route('/pagina/Carrito')
@login_required
def carrito_page():
    # 1. Obtener el carrito de la sesión
    session_cart = session.get('cart', {})

    productos_en_carrito = []
    subtotal = 0
    item_count = 0
    envio = 50.00

    # 2. Procesar el carrito
    for product_id, cantidad in session_cart.items():
        if product_id in PRODUCTOS_DB:
            producto = PRODUCTOS_DB[product_id]
            precio_total_item = producto['precio'] * cantidad

            productos_en_carrito.append({
                "id": product_id,
                "nombre": producto['nombre'],
                "precio_unitario": producto['precio'],
                "cantidad": cantidad,
                "precio_total": precio_total_item,
                "imagen_placeholder": producto['imagen_placeholder']
            })

            subtotal += precio_total_item
            item_count += cantidad

    total = subtotal + envio if productos_en_carrito else 0
    if not productos_en_carrito: envio = 0

    resumen = {
        "subtotal": subtotal,
        "envio": envio,
        "total": total,
        "item_count": item_count
    }

    return render_template(
        'carrito.html',
        categorias=CATEGORIAS_MENU,
        page_name="Carrito",
        productos_en_carrito=productos_en_carrito,
        resumen=resumen,
        colores=COLORES
    )


@app.route('/pagina/<page_name>')
@login_required
def show_page(page_name):
    page_map = {
        "Salud": {"data": None, "title": "Salud"},
        "Bebés": {"data": BEBES_DATA, "title": "Bebés"},
        "VitaminasySuplementos": {"data": VITAMINAS_SUPLEMENTOS_DATA, "title": "Vitaminas y Suplementos"},
        "Ayuda": {"data": AYUDA_DATA, "title": "Ayuda"},
    }

    if page_name == "Antibioticos":
        return antibioticos_page()
    elif page_name == "Carrito":
        return carrito_page()

    if page_name in page_map:
        page_info = page_map[page_name]
        if page_info["data"] is not None:
            return render_template(
                'categoria_generica.html',
                categorias=CATEGORIAS_MENU,
                page_title=page_info["title"],
                sub_categories=page_info["data"],
                colores=COLORES
            )
        else:
            return render_template('pagina_generica.html', page_name=page_name, colores=COLORES)

    return render_template('pagina_generica.html', page_name=page_name, colores=COLORES)


# ----------------------------------------
# RUTAS DEL CARRITO (AÑADIR / QUITAR)
# ----------------------------------------

@app.route('/add_to_cart/<product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    cart = session.get('cart', {})

    if product_id not in PRODUCTOS_DB:
        flash("Error: Producto no encontrado.", "error")
        return redirect(request.referrer or url_for('home'))

    # 1. Obtenemos la cantidad del formulario (si falla, usamos 1 por defecto)
    try:
        cantidad = int(request.form.get('quantity', 1))
    except ValueError:
        cantidad = 1

    # 2. Validamos que no sea menor a 1
    if cantidad < 1:
        cantidad = 1

    # 3. Sumamos la cantidad seleccionada
    cart[product_id] = cart.get(product_id, 0) + cantidad

    session['cart'] = cart
    session.modified = True

    producto = PRODUCTOS_DB[product_id]
    mensaje = f"Has añadido {cantidad} x {producto['nombre']} al carrito."
    flash(mensaje, "cart_modal")

    return redirect(request.referrer or url_for('home'))


@app.route('/remove_from_cart/<product_id>')
@login_required
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if product_id in cart:
        cart.pop(product_id)
        session['cart'] = cart
        session.modified = True
        flash("Producto eliminado del carrito.", "info")
    return redirect(url_for('carrito_page'))


@app.route('/clear_cart')
@login_required
def clear_cart():
    session.pop('cart', None)
    flash("El carrito ha sido vaciado.", "info")
    return redirect(url_for('carrito_page'))

# Eliminamos app.run() para producción