from flask import Flask, render_template, request, redirect, url_for, flash, session, Response, jsonify
from flask import send_from_directory
from flask_pymongo import PyMongo
from bson import ObjectId
from werkzeug.utils import secure_filename
import os
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from bson.json_util import dumps
app = Flask(__name__)
app.secret_key = "supersecretkey"  # Necesario para usar flash messages


# Configuración de la conexión a MongoDB
app.config["MONGO_URI"] = "mongodb://localhost:27017/market-health"
mongo = PyMongo(app)
db_consultas = mongo.db.Consultas



# Configuración para el manejo de archivos y extensiones permitidas
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}  # Permitimos más tipos de archivos

# Crear la carpeta 'uploads' si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

# Función para verificar si la extensión del archivo es permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']



# CRUD Control de Cuentas (Admin, Cliente, User) CRUD
@app.route('/')
def index():
    admins = mongo.db.Clientes.find({"rol": "admin"})
    clientes = mongo.db.Clientes.find({"rol": "cliente"})
    users = mongo.db.Clientes.find({"rol": "user"})
    return render_template('pag-principal.html', admins=admins, clientes=clientes, users=users)

# Función auxiliar para verificar si el correo ya está registrado
def email_existe(email):
    return mongo.db.Clientes.find_one({"email": email}) is not None

@app.route('/insertAdmin', methods=['POST'])
def insert_admin():
    nombre = request.form['nombre']
    email = request.form['email']
    password = request.form['password']
    
    if email_existe(email):
        flash("El correo ya está registrado.", "error")
        return redirect(url_for('gestionar_cuentas'))
    
    mongo.db.Clientes.insert_one({
        'nombre': nombre,
        'email': email,
        'password': password,
        'rol': 'admin'
    })
    return redirect(url_for('gestionar_cuentas'))

@app.route('/insertCliente', methods=['POST'])
def insert_cliente():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    email = request.form['email']
    password = request.form['password']
    telefono = request.form['telefono']
    fecha_nacimiento = request.form['fecha_nacimiento']
    genero = request.form['genero']
    
    if email_existe(email):
        flash("El correo ya está registrado.", "error")
        return redirect(url_for('gestionar_cuentas'))
    
    mongo.db.Clientes.insert_one({
        'nombre': nombre,
        'apellido': apellido,
        'email': email,
        'password': password,
        'telefono': telefono,
        'fecha_nacimiento': fecha_nacimiento,
        'genero': genero,
        'rol': 'cliente'
    })
    return redirect(url_for('gestionar_cuentas'))

@app.route('/insertUser', methods=['POST'])
def insert_user():
    nombre = request.form['nombre']
    email = request.form['email']
    password = request.form['password']
    
    if email_existe(email):
        flash("El correo ya está registrado.", "error")
        return redirect(url_for('gestionar_cuentas'))
    
    mongo.db.Clientes.insert_one({
        'nombre': nombre,
        'email': email,
        'password': password,
        'rol': 'user'
    })
    return redirect(url_for('gestionar_cuentas'))

@app.route('/edit/<rol>/<user_id>', methods=['GET', 'POST'])
def edit_user(rol, user_id):
    user = mongo.db.Clientes.find_one({"_id": ObjectId(user_id)})
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        telefono = request.form.get('telefono')
        fecha_nacimiento = request.form.get('fecha_nacimiento')
        genero = request.form.get('genero')
        
        update_data = {'nombre': nombre, 'email': email, 'password': password, 'rol': rol}
        
        if rol == 'cliente':
            update_data.update({'telefono': telefono, 'fecha_nacimiento': fecha_nacimiento, 'genero': genero})
        
        mongo.db.Clientes.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})
        return redirect(url_for('gestionar_cuentas'))
    
    return render_template('edit-cliente.html', user=user, rol=rol)

@app.route('/delete/<user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    mongo.db.Clientes.delete_one({'_id': ObjectId(user_id)})
    return redirect(url_for('gestionar_cuentas'))  # Cambié 'index' por 'gestionar_cuentas'





@app.route('/gestionar_cuentas')
def gestionar_cuentas():
    admins = list(mongo.db.Clientes.find({"rol": "admin"}))  # Convertir cursor a lista
    clientes = list(mongo.db.Clientes.find({"rol": "cliente"}))
    users = list(mongo.db.Clientes.find({"rol": "user"}))

    return render_template('CRUD_ctr-cuenta.html', admins=admins, clientes=clientes, users=users)




# Registro de usuario INCIO-PRINCIPAL
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        email = request.form.get("email")
        password = request.form.get("password")
        telefono = request.form.get("telefono")
        fecha_nacimiento = request.form.get("fecha_nacimiento")
        genero = request.form.get("genero")

        # Verifica si el email ya está registrado
        if email_existe(email):
            flash("El correo ya está registrado. Usa otro.", "error")
            return redirect(url_for("registro"))

        # Crea el usuario en la base de datos
        usuario = {
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "password": password,
            "telefono": telefono,
            "fecha_nacimiento": fecha_nacimiento,
            "genero": genero,
            "rol": "cliente"
        }
        mongo.db.Clientes.insert_one(usuario)

        flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("login"))

    return render_template("registro.html")





# 🔹 RUTA PARA MANEJAR EL LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo_electronico = request.form.get("correo_electronico")
        contrasena = request.form.get("contrasena")

        # Buscar usuario en la base de datos
        usuario = mongo.db.Clientes.find_one({"email": correo_electronico})

        if usuario and usuario["password"] == contrasena:
            # Guardar información del usuario en sesión
            session["usuario"] = usuario["email"]  # Guardar usuario en sesión
            session["nombre_usuario"] = usuario["nombre"]  # Guardar nombre del usuario
            session["rol"] = usuario["rol"]  # Guardar el rol en sesión
            session["correo_usuario"] = usuario["email"]  # Guardar correo electrónico

            flash("Inicio de sesión exitoso.", "success")

            # Redirigir según el rol del usuario
            if usuario["rol"] == "admin":
                return redirect(url_for("gestionar_cuentas"))
            elif usuario["rol"] == "cliente":
                return redirect(url_for("pagina_principal"))
            elif usuario["rol"] == "user":
                return redirect(url_for("crudconsultass"))
            else:
                flash("Rol no reconocido.", "error")
                return redirect(url_for("login"))
        else:
            flash("Correo o contraseña incorrectos.", "error")
            return redirect(url_for("login"))

    return render_template("iniciosesion.html")


# 🔹 RUTA PARA ADMINISTRADORES (GESTIÓN DE CUENTAS)
@app.route("/gestionar-cuentas1")
def gestionar_cuentas1():
    if "usuario" not in session or session.get("rol") != "admin":
        flash("Acceso no autorizado. Inicia sesión como administrador.", "danger")
        return redirect(url_for("login"))

    return render_template("CRUD_ctr-cuenta.html")  # Ajusta el nombre de tu plantilla


# 🔹 RUTA PARA CLIENTES (PÁGINA PRINCIPAL)
@app.route("/pagina-principal")
def pagina_principal():
    if "usuario" not in session or session.get("rol") != "cliente":
        flash("Acceso no autorizado. Inicia sesión como cliente.", "danger")
        return redirect(url_for("login"))

    return render_template("pag-principal.html", 
                           nombre_usuario=session.get("nombre_usuario"),
                           correo_usuario=session.get("correo_usuario"),
                           rol_usuario=session.get("rol"))


# 🔹 RUTA PARA USUARIOS CON ROL "user" (GESTIÓN DE CONSULTAS MÉDICAS)
@app.route("/crudconsultass")
def crudconsultass():
    if "usuario" not in session or session.get("rol") != "user":
        flash("Acceso no autorizado. Inicia sesión como usuario.", "danger")
        return redirect(url_for("login"))

    return render_template("CRUD-consultas.html")

# 🔹 RUTA PARA VISUALIZAR EL PERFIL DEL USUARIO
@app.route('/perfilp')
def perfilp():
    if "usuario" not in session:
        flash("Debes iniciar sesión para ver tu perfil.", "danger")
        return redirect(url_for("login"))

    return render_template('perfil.html',
                           nombre_usuario=session.get("nombre_usuario", "Usuario"),
                           correo_usuario=session.get("correo_usuario", "No disponible"),
                           rol_usuario=session.get("rol_usuario", "No definido"))


# Redirecciones de botones de la pag-principal a sus respectivas interfaces
# Boton Consultas de pag-principal a consultas.html
@app.route('/consultas')
def consultas():
    return render_template('consultas.html',nombre_usuario=session.get("nombre_usuario"))

#Boton de regreso a pag-principal de consultas.hmtl  (Lo mismo con el bt de regreso de productos.html a pag-principal)
@app.route('/principal')
def principal():
    return render_template('pag-principal.html',nombre_usuario=session.get("nombre_usuario"))

# Página principal Boton de inicio de sesion te redirije a iniciosesion.html
@app.route('/paguinaprincipal')
def insesion():
    return render_template('iniciosesion.html',nombre_usuario=session.get("nombre_usuario"))

# Página principal Boton de inicio de sesion te redirije a iniciosesion.html
@app.route('/crudcuen')
def sesion():
    return render_template('iniciosesion.html',nombre_usuario=session.get("nombre_usuario"))

#Paguina principal Boton de productos te redirije a productos.html
@app.route('/productos')
def productos():
    return render_template('productos.html',nombre_usuario=session.get("nombre_usuario"))

#Bt de regreso de CRUD-cuentas a iniciosesio.html
@app.route('/inise')
def inise():
    return render_template('iniciosesion.html',nombre_usuario=session.get("nombre_usuario"))

#Usuario cerrar sesión de pag-pricinpal, te redirige a iniciosesion.hmtl
@app.route("/cerrar-sesion")
def cerrar_sesion():
    session.clear()  # Borra todos los datos de la sesión
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("login"))

#Ruta bt de perfil de pag-principal te redirige a perfilhtml 
@app.route('/perfilpp')
def perfilpp():
        return render_template('perfil.html',
                            nombre_usuario=session.get("nombre_usuario", "Usuario"),
                           fecha_registro=session.get("fecha_registro", ""),
                           correo_usuario=session.get("correo_usuario", "No disponible"),
                           rol_usuario=session.get("rol", "No definido"))





# Ruta para agregar consulta consulta.html
@app.route('/agregar_consulta', methods=['GET', 'POST'])
def agregar_consulta():
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        fecha_consulta = request.form['fecha_consulta']
        hora_consulta = request.form['hora_consulta']
        mensaje = request.form['mensaje']

        historial_medico_path = None  # Inicializar la variable del historial médico

        # Manejo del archivo de historial médico
        if 'historial_medico' in request.files:
            historial_medico = request.files['historial_medico']
            if historial_medico and historial_medico.filename:
                if allowed_file(historial_medico.filename):  # Verificar la extensión
                    filename = secure_filename(historial_medico.filename)
                    historial_medico_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    historial_medico.save(historial_medico_path)
                else:
                    flash('Formato de archivo no permitido. Solo se aceptan imágenes y documentos PDF/DOC.', 'danger')
                    return redirect(url_for('agregar_consulta'))

        # Insertar datos en MongoDB
        consulta = {
            "nombre": nombre,
            "email": email,
            "telefono": telefono,
            "fecha_consulta": fecha_consulta,
            "hora_consulta": hora_consulta,
            "mensaje": mensaje,
            "historial_medico": historial_medico_path
        }

        mongo.db.Consultas.insert_one(consulta)

        # Mensaje de éxito
        flash('¡Consulta registrada con éxito! Nos pondremos en contacto contigo pronto.', 'success')

        return redirect(url_for('agregar_consulta'))

    return render_template('consultas.html')




# CRUD-consultas.html
# Ruta para mostrar y gestionar consultas
@app.route("/crud-consultas", methods=["GET", "POST"])
def crud_consulta():
    consultas = [{**consulta, "_id": str(consulta["_id"])} for consulta in mongo.db.Consultas.find()]  # Convertir cursor a lista
    
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        telefono = request.form["telefono"]
        fecha_consulta = request.form["fecha"]
        hora_consulta = request.form["hora"]
        mensaje = request.form["mensaje"]

        # Manejo del archivo de historial médico
        historial_medico = None
        if 'historial_medico' in request.files:
            archivo = request.files['historial_medico']
            if archivo and allowed_file(archivo.filename):
                filename = secure_filename(archivo.filename)
                archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                historial_medico = f"uploads/{filename}"

        # Insertar la consulta en la base de datos
        mongo.db.Consultas.insert_one({
            "nombre": nombre,
            "email": email,
            "telefono": telefono,
            "fecha_consulta": fecha_consulta,
            "hora_consulta": hora_consulta,
            "mensaje": mensaje,
            "historial_medico": historial_medico
        })
        
        return redirect(url_for("crud_consulta"))  # Redirigir a la misma página después de agregar

    # Pasar las consultas al template
    return render_template("CRUD-consultas.html", consultas=consultas)      # Siempre devuelve la lista

# Ruta para eliminar una consulta
@app.route("/delete-consulta/<consulta_id>", methods=["POST"])
def delete_consulta(consulta_id):
    mongo.db.Consultas.delete_one({"_id": ObjectId(consulta_id)})
    return redirect(url_for("crud_consulta"))

# Ruta para editar una consulta
@app.route("/edit-consulta/<consulta_id>", methods=["GET", "POST"])
def edit_consulta(consulta_id):
    consulta = mongo.db.Consultas.find_one({"_id": ObjectId(consulta_id)})
    
    if request.method == "POST":
        mongo.db.Consultas.update_one({"_id": ObjectId(consulta_id)}, {"$set": {
            "nombre": request.form["nombre"],
            "email": request.form["email"],
            "telefono": request.form["telefono"],
            "fecha_consulta": request.form["fecha"],
            "hora_consulta": request.form["hora"],
            "mensaje": request.form["mensaje"]
        }})
        return redirect(url_for("crud_consulta"))  # Redirigir después de la edición
    
    return render_template("edit-consulta.html", consulta=consulta)

# Para mostrar los archivos subidos, sirve el archivo si es solicitado
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



@app.route('/plan-alimentacion')
def plan_alimentacion():
    return render_template('plan_alimentacion.html')

@app.route('/contactos')
def contactos():
    return render_template('contacto.html')

@app.route('/pago')
def pago():
    return render_template('pago.html') 

@app.route('/procesar_pago', methods=['POST'])
def procesar_pago():
    return "Pago procesado con éxito. ¡Gracias por tu compra!"

@app.route("/perfil")
def perfil():
    # Simulación de datos; reemplázalos por los datos reales de tu sistema.
    datos_usuario = {
        "nombre_usuario": "Kevin",
        "correo_usuario": "kevin@example.com",
        "rol_usuario": "Cliente",
        "fecha_registro": "23 de marzo de 2025"
    }

    return render_template(
        "perfil.html",
        nombre_usuario=datos_usuario["nombre_usuario"],
        correo_usuario=datos_usuario["correo_usuario"],
        rol_usuario=datos_usuario["rol_usuario"],
        fecha_registro=datos_usuario["fecha_registro"]
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
 