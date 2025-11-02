from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import re

# Inicialización de la aplicación Flask
app = Flask(__name__)

# --- CONFIGURACIÓN DE LA BASE DE DATOS Y SESIÓN ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///farmacia.db'
app.config['SECRET_KEY'] = 'tu_clave_secreta_super_segura_42'
db = SQLAlchemy(app)


# ----------------------------------------
# MODELO DE USUARIO
# ----------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

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

# --- Paleta de colores y Datos ---
COLOR_VERDE_MENTA = "#A1E8D5"
COLOR_AZUL_CIELO = "#87CEFA"
COLOR_GRIS_CALIDO = "#F0F0F0"
COLOR_BLANCO = "#FFFFFF"
COLOR_ROJO_CORAL = "#FF6347"
COLOR_AZUL_OSCURO = "#003366"

CATEGORIAS_MENU = ["Salud", "Bebés", "Vitaminas y Suplementos", "Ayuda"]

PRODUCTOS_DESTACADOS = [
    {"nombre": "Analgésico", "precio": "99.00", "imagen_placeholder": "Analgesico"},
    {"nombre": "Multivitamínico", "precio": "180.50", "imagen_placeholder": "Multivitaminico"},
    {"nombre": "Protector Solar", "precio": "150.00", "imagen_placeholder": "ProtectorSolar"},
    {"nombre": "Vitamina C", "precio": "120.00", "imagen_placeholder": "VitaminaC"},
]

CATEGORIAS_EXTENDIDAS = [
    ("Cuidado de la Piel", "🧴", "Productos para el rostro y cuerpo."),
    ("Primeros Auxilios", "🩹", "Kits esenciales para emergencias."),
    ("Nutrición Deportiva", "💪", "Proteínas, barras y suplementos."),
    ("Medicina Natural", "🌿", "Opciones homeopáticas y herbolarias."),
    ("Salud Visual", "👁️", "Lentes de contacto y gotas."),
    ("Higiene Personal", "🧼", "Jabones, champús y desodorantes."),
]

ANTIBIOTICOS_DATA = [
    {"nombre": "Amoxicilina 500mg", "precio": "85.00", "imagen_placeholder": "Amoxicilina"},
    {"nombre": "Azitromicina 250mg", "precio": "130.00", "imagen_placeholder": "Azitromicina"},
    {"nombre": "Ciprofloxacino", "precio": "110.00", "imagen_placeholder": "Ciprofloxacino"},
    {"nombre": "Metronidazol", "precio": "75.00", "imagen_placeholder": "Metronidazol"},
]

BEBES_DATA = ["Fórmulas Infantiles", "Pañales", "Cuidado del Bebé", "Alimentos para Bebé"]
VITAMINAS_SUPLEMENTOS_DATA = ["Complementos Alimenticios", "Multivitaminas", "Suplementos Alimenticios"]
AYUDA_DATA = ["Contáctanos", "Preguntas Frecuentes", "Localizador de SuperFarmacias"]

CARRITO_DATA = {
    "productos": [
        {"nombre": "Amoxicilina 500mg", "precio": 85.00, "cantidad": 2},
        {"nombre": "Protector Solar", "precio": 150.00, "cantidad": 1},
        {"nombre": "Vitamina C", "precio": 120.00, "cantidad": 1},
    ],
    "envio": 50.00
}


def calcular_total_carrito(data):
    subtotal = sum(item["precio"] * item["cantidad"] for item in data["productos"])
    envio = data["envio"]
    total = subtotal + envio
    return {"subtotal": subtotal, "envio": envio, "total": total,
            "item_count": sum(item["cantidad"] for item in data["productos"])}


CARRITO_RESUMEN = calcular_total_carrito(CARRITO_DATA)

COLORES = {
    "verde_menta": COLOR_VERDE_MENTA,
    "azul_cielo": COLOR_AZUL_CIELO,
    "gris_calido": COLOR_GRIS_CALIDO,
    "blanco": COLOR_BLANCO,
    "rojo_coral": COLOR_ROJO_CORAL,
    "azul_oscuro": COLOR_AZUL_OSCURO
}


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
        confirm_password = request.form.get('confirm_password')  # NUEVO
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        address = request.form.get('address')
        phone_number = request.form.get('phone_number')

        # 1. Validación de campos requeridos y unicidad
        if not username or not password or not full_name or not email or not confirm_password:
            return render_template('register.html', error="Todos los campos con (*) son requeridos.", colores=COLORES)

        # 1.1. VALIDACIÓN: Confirmar contraseña
        if password != confirm_password:
            return render_template('register.html', error="Error: Las contraseñas ingresadas no coinciden.",
                                   colores=COLORES)

        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Error: El nombre de usuario ya está registrado.",
                                   colores=COLORES)

        if User.query.filter_by(email=email).first():
            return render_template('register.html', error="Error: El email ya está registrado.", colores=COLORES)

        # 2. Validación de Contraseña Segura
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
            error_msg = "La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula, un número y un símbolo (@$!%*?&)."
            return render_template('register.html', error=error_msg, colores=COLORES)

        # 3. Creación y guardado del usuario
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
        email = request.form.get('email')

        # Simulación de proceso de envío de correo
        flash(
            "Si el correo electrónico está registrado, recibirás un enlace para restablecer tu contraseña. (Función simulada)",
            "info")
        return redirect(url_for('login'))

    return render_template('forgot_password.html', colores=COLORES)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))


# ----------------------------------------
# RUTAS DE NAVEGACIÓN PROTEGIDAS
# ----------------------------------------

@app.route('/')
@login_required
def home():
    return render_template(
        'index.html',
        categorias=CATEGORIAS_MENU,
        productos=PRODUCTOS_DESTACADOS,
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
    return render_template(
        'antibioticos.html',
        categorias=CATEGORIAS_MENU,
        productos_antibioticos=ANTIBIOTICOS_DATA,
        colores=COLORES
    )


@app.route('/pagina/Carrito')
@login_required
def carrito_page():
    return render_template(
        'carrito.html',
        categorias=CATEGORIAS_MENU,
        page_name="Carrito",
        carrito=CARRITO_DATA,
        resumen=CARRITO_RESUMEN,
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


if __name__ == '__main__':
    app.run(debug=True)