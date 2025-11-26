import os
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import re

app = Flask(__name__)

# --- CONFIGURACIÓN ---
DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///farmacia.db')
if DATABASE_URI.startswith("postgres://"):
    DATABASE_URI = DATABASE_URI.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave_local_de_prueba')

db = SQLAlchemy(app)


# --- MODELO USER ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
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

# --- DATOS ESTÁTICOS ---
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

# --- BASE DE DATOS DE PRODUCTOS ---
PRODUCTOS_DB = {
    # --- DESTACADOS ---
    'p1': {"id": "p1", "nombre": "Analgésico", "precio": 99.00, "imagen_placeholder": "Analgesico"},
    'p2': {"id": "p2", "nombre": "Multivitamínico", "precio": 180.50, "imagen_placeholder": "Multivitaminico"},
    'p3': {"id": "p3", "nombre": "Protector Solar", "precio": 150.00, "imagen_placeholder": "ProtectorSolar"},
    'p4': {"id": "p4", "nombre": "Vitamina C", "precio": 120.00, "imagen_placeholder": "VitaminaC"},

    # --- ANTIBIÓTICOS (Actualizado con Subcategorías) ---
    # Subcats: 'penicilinas', 'macrolidos', 'respiratorio', 'estomacal'
    'a1': {"id": "a1", "nombre": "Amoxicilina 500mg", "precio": 85.00, "imagen_placeholder": "Amoxicilina",
           "subcategoria": "penicilinas"},
    'a2': {"id": "a2", "nombre": "Azitromicina 3 Tabs", "precio": 130.00, "imagen_placeholder": "Azitromicina",
           "subcategoria": "macrolidos"},
    'a3': {"id": "a3", "nombre": "Levofloxacino 750mg", "precio": 180.00, "imagen_placeholder": "Levofloxacino",
           "subcategoria": "respiratorio"},
    'a4': {"id": "a4", "nombre": "Metronidazol", "precio": 75.00, "imagen_placeholder": "Metronidazol",
           "subcategoria": "estomacal"},
    'a5': {"id": "a5", "nombre": "Ampicilina 500mg", "precio": 60.00, "imagen_placeholder": "Ampicilina",
           "subcategoria": "penicilinas"},
    'a6': {"id": "a6", "nombre": "Claritromicina", "precio": 210.00, "imagen_placeholder": "Claritromicina",
           "subcategoria": "macrolidos"},
    'a7': {"id": "a7", "nombre": "Ceftriaxona Inyectable", "precio": 150.00, "imagen_placeholder": "Ceftriaxona",
           "subcategoria": "respiratorio"},
    'a8': {"id": "a8", "nombre": "Ciprofloxacino", "precio": 95.00, "imagen_placeholder": "Ciprofloxacino",
           "subcategoria": "estomacal"},

    # --- SALUD E HIGIENE (Actualizado con Subcategorías) ---
    # Subcats: 'equipo', 'auxilios', 'higiene', 'ortopedia'
    's1': {"id": "s1", "nombre": "Cubrebocas KN95 (Paq. 10)", "precio": 150.00, "imagen_placeholder": "Cubrebocas",
           "subcategoria": "higiene"},
    's2': {"id": "s2", "nombre": "Gel Antibacterial 1L", "precio": 85.00, "imagen_placeholder": "GelAnti",
           "subcategoria": "higiene"},
    's3': {"id": "s3", "nombre": "Termómetro Digital", "precio": 220.00, "imagen_placeholder": "Termometro",
           "subcategoria": "equipo"},
    's4': {"id": "s4", "nombre": "Alcohol Etílico 70°", "precio": 45.00, "imagen_placeholder": "Alcohol",
           "subcategoria": "auxilios"},
    's5': {"id": "s5", "nombre": "Vendas Elásticas 10cm", "precio": 15.00, "imagen_placeholder": "Vendas",
           "subcategoria": "auxilios"},
    's6': {"id": "s6", "nombre": "Oxímetro de Pulso", "precio": 350.00, "imagen_placeholder": "Oximetro",
           "subcategoria": "equipo"},
    's7': {"id": "s7", "nombre": "Baumanómetro Digital", "precio": 650.00, "imagen_placeholder": "Baumanometro",
           "subcategoria": "equipo"},
    's8': {"id": "s8", "nombre": "Curitas (Caja 20pz)", "precio": 35.00, "imagen_placeholder": "Curitas",
           "subcategoria": "auxilios"},
    's9': {"id": "s9", "nombre": "Collarín Blando", "precio": 280.00, "imagen_placeholder": "Collarin",
           "subcategoria": "ortopedia"},
    's10': {"id": "s10", "nombre": "Muletas de Aluminio", "precio": 450.00, "imagen_placeholder": "Muletas",
            "subcategoria": "ortopedia"},

    # --- BEBÉS ---
    'b1': {"id": "b1", "nombre": "Fórmula NAN 1 (800g)", "precio": 450.00, "imagen_placeholder": "Nan1",
           "subcategoria": "formulas"},
    'b2': {"id": "b2", "nombre": "Enfamil Confort", "precio": 520.00, "imagen_placeholder": "Enfamil",
           "subcategoria": "formulas"},
    'b3': {"id": "b3", "nombre": "Pañales Huggies RN (30pz)", "precio": 180.00, "imagen_placeholder": "HuggiesRN",
           "subcategoria": "panales"},
    'b4': {"id": "b4", "nombre": "Pañales BioBaby Etapa 3", "precio": 210.00, "imagen_placeholder": "BioBaby",
           "subcategoria": "panales"},
    'b5': {"id": "b5", "nombre": "Shampoo Ricitos de Oro", "precio": 65.00, "imagen_placeholder": "ShampooBebe",
           "subcategoria": "cuidado"},
    'b6': {"id": "b6", "nombre": "Toallitas Húmedas (Paq. 4)", "precio": 120.00, "imagen_placeholder": "Toallitas",
           "subcategoria": "cuidado"},
    'b7': {"id": "b7", "nombre": "Gerber de Manzana", "precio": 18.00, "imagen_placeholder": "Gerber",
           "subcategoria": "alimentos"},
    'b8': {"id": "b8", "nombre": "Cereal Infantil Nestum", "precio": 45.00, "imagen_placeholder": "Cereal",
           "subcategoria": "alimentos"},

    # --- VITAMINAS Y SUPLEMENTOS ---
    'v1': {"id": "v1", "nombre": "Centrum Performance", "precio": 280.00, "imagen_placeholder": "Centrum",
           "subcategoria": "multi"},
    'v2': {"id": "v2", "nombre": "Redoxon Vitamina C", "precio": 110.00, "imagen_placeholder": "Redoxon",
           "subcategoria": "multi"},
    'v3': {"id": "v3", "nombre": "Proteína Whey Gold 1kg", "precio": 850.00, "imagen_placeholder": "WheyProtein",
           "subcategoria": "deportiva"},
    'v4': {"id": "v4", "nombre": "Creatina Monohidratada", "precio": 320.00, "imagen_placeholder": "Creatina",
           "subcategoria": "deportiva"},
    'v5': {"id": "v5", "nombre": "Melatonina 5mg (Sueño)", "precio": 140.00, "imagen_placeholder": "Melatonina",
           "subcategoria": "natural"},
    'v6': {"id": "v6", "nombre": "Omega 3 (Aceite de Salmón)", "precio": 210.00, "imagen_placeholder": "Omega3",
           "subcategoria": "natural"},
}

# Listas de IDs
PRODUCTOS_DESTACADOS_IDS = ['p1', 'p2', 'p3', 'p4']
ANTIBIOTICOS_DATA_IDS = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8']
SALUD_DATA_IDS = ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10']
BEBES_DATA_IDS = ['b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8']
VITAMINAS_DATA_IDS = ['v1', 'v2', 'v3', 'v4', 'v5', 'v6']

CATEGORIAS_EXTENDIDAS = [
    ("Cuidado de la Piel", "🧴", "Productos para el rostro y cuerpo."),
    ("Primeros Auxilios", "🩹", "Kits esenciales para emergencias."),
    ("Nutrición Deportiva", "💪", "Proteínas, barras y suplementos."),
    ("Medicina Natural", "🌿", "Opciones homeopáticas y herbolarias."),
    ("Salud Visual", "👁️", "Lentes de contacto y gotas."),
    ("Higiene Personal", "🧼", "Jabones, champús y desodorantes."),
]

AYUDA_DATA = ["Contáctanos", "Preguntas Frecuentes", "Localizador de SuperFarmacias"]


# --- SEGURIDAD ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash("Necesitas iniciar sesión para acceder a esta página.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@app.context_processor
def inject_user():
    return dict(logged_in=session.get('logged_in'), username=session.get('username'))


# --- RUTAS AUTH ---
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
            return render_template('register.html', error="Campos requeridos faltantes.", colores=COLORES)
        if password != confirm_password:
            return render_template('register.html', error="Las contraseñas no coinciden.", colores=COLORES)
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Usuario ya registrado.", colores=COLORES)
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error="Email ya registrado.", colores=COLORES)
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
            return render_template('register.html', error="Contraseña insegura.", colores=COLORES)

        new_user = User(username=username, full_name=full_name, email=email, address=address, phone_number=phone_number)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        session['logged_in'] = True
        session['username'] = username
        return redirect(url_for('home'))
    return render_template('register.html', colores=COLORES)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session: return redirect(url_for('home'))
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
        flash("Se ha enviado un enlace a tu correo.", "info")
        return redirect(url_for('login'))
    return render_template('forgot_password.html', colores=COLORES)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))


# --- RUTAS DE NAVEGACIÓN ---

@app.route('/')
@login_required
def home():
    productos_completos = [PRODUCTOS_DB[pid] for pid in PRODUCTOS_DESTACADOS_IDS if pid in PRODUCTOS_DB]
    return render_template('index.html', categorias=CATEGORIAS_MENU, productos=productos_completos,
                           categorias_extendidas=CATEGORIAS_EXTENDIDAS, colores=COLORES)


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', categorias=CATEGORIAS_MENU, colores=COLORES)


# --- CATEGORÍA: ANTIBIÓTICOS (Con Filtros) ---
@app.route('/pagina/Antibioticos')
@login_required
def antibioticos_page():
    filtro_actual = request.args.get('filtro')
    productos_anti = [PRODUCTOS_DB[pid] for pid in ANTIBIOTICOS_DATA_IDS if pid in PRODUCTOS_DB]

    if filtro_actual:
        productos_anti = [p for p in productos_anti if p.get('subcategoria') == filtro_actual]

    return render_template('antibioticos.html', categorias=CATEGORIAS_MENU, productos=productos_anti,
                           filtro_actual=filtro_actual, colores=COLORES)


# --- CATEGORÍA: SALUD (Con Filtros) ---
@app.route('/pagina/Salud')
@login_required
def salud_page():
    filtro_actual = request.args.get('filtro')
    productos_salud = [PRODUCTOS_DB[pid] for pid in SALUD_DATA_IDS if pid in PRODUCTOS_DB]

    if filtro_actual:
        productos_salud = [p for p in productos_salud if p.get('subcategoria') == filtro_actual]

    return render_template('salud.html', categorias=CATEGORIAS_MENU, productos=productos_salud,
                           filtro_actual=filtro_actual, colores=COLORES)


# --- CATEGORÍA: BEBÉS ---
@app.route('/pagina/Bebes')
@login_required
def bebes_page():
    filtro_actual = request.args.get('filtro')
    productos_bebes = [PRODUCTOS_DB[pid] for pid in BEBES_DATA_IDS if pid in PRODUCTOS_DB]
    if filtro_actual:
        productos_bebes = [p for p in productos_bebes if p.get('subcategoria') == filtro_actual]
    return render_template('bebes.html', categorias=CATEGORIAS_MENU, productos=productos_bebes,
                           filtro_actual=filtro_actual, colores=COLORES)


# --- CATEGORÍA: VITAMINAS ---
@app.route('/pagina/VitaminasySuplementos')
@login_required
def vitaminas_page():
    filtro_actual = request.args.get('filtro')
    productos_vit = [PRODUCTOS_DB[pid] for pid in VITAMINAS_DATA_IDS if pid in PRODUCTOS_DB]
    if filtro_actual:
        productos_vit = [p for p in productos_vit if p.get('subcategoria') == filtro_actual]
    return render_template('vitaminas.html', categorias=CATEGORIAS_MENU, productos=productos_vit,
                           filtro_actual=filtro_actual, colores=COLORES)


@app.route('/pagina/Carrito')
@login_required
def carrito_page():
    session_cart = session.get('cart', {})
    productos_en_carrito = []
    subtotal = 0
    item_count = 0
    for product_id, cantidad in session_cart.items():
        if product_id in PRODUCTOS_DB:
            producto = PRODUCTOS_DB[product_id]
            precio_total = producto['precio'] * cantidad
            productos_en_carrito.append({
                "id": product_id, "nombre": producto['nombre'], "precio_unitario": producto['precio'],
                "cantidad": cantidad, "precio_total": precio_total, "imagen_placeholder": producto['imagen_placeholder']
            })
            subtotal += precio_total
            item_count += cantidad
    total = subtotal + 50.00 if productos_en_carrito else 0
    return render_template('carrito.html', categorias=CATEGORIAS_MENU, page_name="Carrito",
                           productos_en_carrito=productos_en_carrito,
                           resumen={"subtotal": subtotal, "envio": 50.00 if productos_en_carrito else 0, "total": total,
                                    "item_count": item_count}, colores=COLORES)


@app.route('/pagina/<page_name>')
@login_required
def show_page(page_name):
    page_map = {"Ayuda": {"data": AYUDA_DATA, "title": "Ayuda"}}
    if page_name == "Antibioticos":
        return antibioticos_page()
    elif page_name == "Salud":
        return salud_page()
    elif page_name == "Bebés":
        return bebes_page()
    elif page_name == "VitaminasySuplementos":
        return vitaminas_page()
    elif page_name == "Carrito":
        return carrito_page()

    if page_name in page_map:
        return render_template('categoria_generica.html', categorias=CATEGORIAS_MENU,
                               page_title=page_map[page_name]["title"], sub_categories=page_map[page_name]["data"],
                               colores=COLORES)
    return render_template('pagina_generica.html', page_name=page_name, colores=COLORES)


# --- ACCIONES CARRITO ---
@app.route('/add_to_cart/<product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    cart = session.get('cart', {})
    if product_id not in PRODUCTOS_DB: return redirect(url_for('home'))
    try:
        cantidad = int(request.form.get('quantity', 1))
    except ValueError:
        cantidad = 1
    if cantidad < 1: cantidad = 1
    cart[product_id] = cart.get(product_id, 0) + cantidad
    session['cart'] = cart
    session.modified = True
    flash(f"Has añadido {cantidad} x {PRODUCTOS_DB[product_id]['nombre']} al carrito.", "cart_modal")
    return redirect(request.referrer or url_for('home'))


@app.route('/remove_from_cart/<product_id>')
@login_required
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if product_id in cart:
        cart.pop(product_id)
        session['cart'] = cart
        session.modified = True
        flash("Producto eliminado.", "info")
    return redirect(url_for('carrito_page'))


@app.route('/clear_cart')
@login_required
def clear_cart():
    session.pop('cart', None)
    flash("Carrito vaciado.", "info")
    return redirect(url_for('carrito_page'))