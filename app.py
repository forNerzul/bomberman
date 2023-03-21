from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#creamos nuestra aplicacion app
app = Flask(__name__)
#indica un recurso, indica que usamos sqlite como motor y luego el nombre de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base_de_datos.db'
#nos da seguridad en la base de datos 
app.config['SECRET_KEY'] = 'pollo_frito'

#instanciamos nuestra base de datos
db = SQLAlchemy(app)


#modelos
class Movil(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # unique= True que sea un registro unico y que no se pueda repetir (si se puede editar pero no repetir)
    #nullable= true nos permite que pueda ser nulo o vacio
    n_movil = db.Column(db.String(80), unique=True, nullable=False)
    cuartel = db.Column(db.String(80), unique=False, nullable=False)
    tipo = db.Column(db.String(80), unique=False, nullable=False)
    #default nos permite poner un valor por defecto
    estado = db.Column(db.String(80), unique=False, default='disponible', nullable=False)

class Incidente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    operador = db.Column(db.String(80), unique=False, nullable=False)
    #db.ForeignKey('movil.id') establecemos una relacion con movil.id para proporcionarle si o si un movil a cada incidente, es foraneo porque no pertenece a esta tabla y hace referencia a la tabla de movil --> movil.id
    movil_id = db.Column(db.Integer, db.ForeignKey('movil.id'), nullable=False)
    #es con m minuscula ya que si queremos una ForeignKey para referirse al id de una clase en general debe escribirse siempre todo en minuscula para evitar conflicto
    servicio = db.Column(db.String(80), unique=False, nullable=False)
    tipo_servicio = db.Column(db.String(80), unique=False, nullable=False)
    salida = db.Column(db.DateTime, nullable=True)
    llegada = db.Column(db.DateTime, nullable=True)
    lugar = db.Column(db.String(80), unique=False, nullable=False)
    observaciones = db.Column(db.String(80), unique=False, nullable=False)
    estado = db.Column(db.String(80), unique=False, default="en progreso", nullable=False)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/movil', methods = ['GET', 'POST'])
def crear_movil():
    if request.method == 'POST':
        n_movil = request.form['n_movil']
        cuartel = request.form['cuartel']
        tipo = request.form['tipo']
        movil = Movil(n_movil=n_movil, cuartel=cuartel, tipo=tipo)
        #creando un movil a traves de Movil y con add agregamos a nuestra session de nuestra db
        db.session.add(movil)
        #con el commit grabamos esos cambios a la db
        db.session.commit()
        return redirect(url_for('moviles'))
    return render_template('crear_movil.html')

@app.route('/moviles')
def moviles():
    moviles = Movil.query.all()
    return render_template('listar_moviles.html', moviles=moviles)
#<int:movil_id> con esto recibimos movil_id con query params
@app.route('/moviles/<int:movil_id>/cambiar_estado', methods=['POST'])
def cambiar_estado(movil_id):
    movil = Movil.query.get_or_404(movil_id)
    nuevo_estado = request.form['estado']
    movil.estado = nuevo_estado
    #con esto guardamos en la base de datos 
    db.session.commit()
    return redirect(url_for('moviles'))

@app.route('/incidentes/cambiar_estado', methods=['GET', 'POST'])
def cambiar_estado_incidente():
    if request.method == 'POST':
        #request traemos los datos del formulario a traves del atributo name de nuestro formulario
        incidente_id = request.form['incidente_id']
        #con el query buscamos la informacion en la tabla de Incidente a traves del incidente_id  y que si no trae nos arroje un error 404
        incidente = Incidente.query.get_or_404(incidente_id)
        nuevo_estado = request.form['estado']
        incidente.estado = nuevo_estado
        #agregamos con session a la base de datos ese nuevo estado en incidente
        db.session.commit()
        if nuevo_estado == 'finalizado':
            movil = Movil.query.get_or_404(incidente.movil_id)
            movil.estado = 'disponible'
            db.session.commit()
        #redirect 
        return redirect(url_for('incidentes'))
    return redirect(url_for('incidentes'))

@app.route('/disponibles')
def disponibles():
    #un filtro de acuerdo a cada cuartel o todos los cuarteles
    cuartel = request.args.get('cuartel', 'Todos', type=str)
    
    if cuartel == 'Todos':
        moviles = Movil.query.filter_by(estado='disponible').all()
    else:
        moviles = Movil.query.filter_by(estado='disponible').filter(Movil.cuartel == cuartel).all()
    #aca generamos las opciones que se ven en nuestra pantalla para que cree de manera unica cada cuartel 
    moviles_filter = Movil.query.filter_by(estado='disponible').all()
    cuarteles = ['Todos']
    for movil in moviles_filter:
        if movil.cuartel not in cuarteles:
            cuarteles.append(movil.cuartel)

    return render_template('listar_moviles_disponibles.html', moviles=moviles, cuarteles=cuarteles)

@app.route('/incidente', methods = ['GET', 'POST'])
def crear_incidente():
    #se obtiene el numero de movil a traves de los argumentos
    n_movil = request.args.get('n_movil', None, type=str)

    if n_movil is None:
        return redirect(url_for('disponibles'))
    movil_id = Movil.query.filter_by(n_movil=n_movil).first().id
    
    if request.method == 'POST':
        operador = request.form['operador']
        servicio = request.form['servicio']
        tipo_servicio = request.form['tipo_servicio']
        #'%Y-%m-%dT%H:%M' es la forma que quiero que se vea la fecha y hora
        salida = datetime.strptime(request.form['salida'], '%Y-%m-%dT%H:%M')
        llegada = datetime.strptime(request.form['llegada'], '%Y-%m-%dT%H:%M')
        lugar = request.form['lugar']
        observaciones = request.form['observaciones']
        try :
            movil = Movil.query.get_or_404(movil_id)
            movil.estado = 'en uso'
            db.session.commit()
        except:
            redirect(url_for('disponibles'))

        incidente = Incidente(operador=operador, movil_id=movil_id, servicio=servicio, tipo_servicio=tipo_servicio, salida=salida, llegada=llegada, lugar=lugar, observaciones=observaciones)
        db.session.add(incidente)
        db.session.commit()
        return redirect(url_for('incidentes'))
    return render_template('crear_incidente.html', n_movil=n_movil)


@app.route('/incidentes')
def incidentes():
    incidentes = Incidente.query.all()
    return render_template('listar_incidentes.html', incidentes=incidentes)

with app.app_context():
    db.create_all()
# run the app
if __name__ == '__main__':
    app.run( debug=True, port='3000')
