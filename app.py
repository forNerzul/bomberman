from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base_de_datos.db'
app.config['SECRET_KEY'] = 'pollo_frito'
db = SQLAlchemy(app)

# change temoplate folder
app.template_folder = 'views'

#modelos
class Movil(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    n_movil = db.Column(db.String(80), unique=True, nullable=False)
    cuartel = db.Column(db.String(80), unique=False, nullable=False)
    tipo = db.Column(db.String(80), unique=False, nullable=False)
    estado = db.Column(db.String(80), unique=False, default='disponible', nullable=True)

    def getAll():
        return Movil.query.all()
    
    def getOne(id):
        return Movil.query.get_or_404(id)
    
    def getDisponibles():
        return Movil.query.filter_by(estado='disponible').all()
    
    def getDisponiblesByCuartel(cuartel):
        return Movil.query.filter_by(estado='disponible').filter(Movil.cuartel == cuartel).all()
    
    def setState(self, state):
        self.estado = state
        db.session.commit()
    
    def getAllCuarteles():
        cuarteles = ['Todos']
        moviles = Movil.query.filter_by(estado='disponible').all()
        for movil in moviles:
            if movil.cuartel not in cuarteles:
                cuarteles.append(movil.cuartel)
        return cuarteles
    
    def createAndCommit(n_movil, cuartel, tipo):
        movil = Movil(n_movil=n_movil, cuartel=cuartel, tipo=tipo)
        db.session.add(movil)
        db.session.commit()

    def getMovilByN_movil(n_movil):
        movil = Movil.query.filter_by(n_movil=n_movil).first()
        return movil
        
class Incidente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    operador = db.Column(db.String(80), unique=False, nullable=False)
    movil_id = db.Column(db.Integer, db.ForeignKey('movil.id'), nullable=False)
    servicio = db.Column(db.String(80), unique=False, nullable=False)
    tipo_servicio = db.Column(db.String(80), unique=False, nullable=False)
    salida = db.Column(db.DateTime, nullable=True)
    llegada = db.Column(db.DateTime, nullable=True)
    lugar = db.Column(db.String(80), unique=False, nullable=False)
    observaciones = db.Column(db.String(80), unique=False, nullable=False)
    estado = db.Column(db.String(80), unique=False, default="en progreso", nullable=False)

    def getAll():
        return Incidente.query.all()
    
    def getOne(id):
        return Incidente.query.get_or_404(id)
    
    def setState(self, state):
        self.estado = state
        db.session.commit()

    def createAndCommit(operador, movil_id, servicio, tipo_servicio, salida, llegada, lugar, observaciones):
        incidente = Incidente(operador=operador, movil_id=movil_id, servicio=servicio, tipo_servicio=tipo_servicio, salida=salida, llegada=llegada, lugar=lugar, observaciones=observaciones)
        db.session.add(incidente)
        db.session.commit()





@app.route('/')
def home():
    return render_template('home.html')

@app.route('/movil', methods = ['GET', 'POST'])
def crear_movil():
    if request.method == 'POST':
        n_movil = request.form['n_movil']
        cuartel = request.form['cuartel']
        tipo = request.form['tipo']
        Movil.createAndCommit(n_movil, cuartel, tipo)
        return redirect(url_for('moviles'))
    return render_template('crear_movil.html')

@app.route('/moviles')
def moviles():
    moviles = Movil.getAll()
    return render_template('listar_moviles.html', moviles=moviles)

@app.route('/moviles/<int:movil_id>/cambiar_estado', methods=['POST'])
def cambiar_estado(movil_id):
    nuevo_estado = request.form['estado']
    movil = Movil.getOne(movil_id)
    movil.setState(nuevo_estado)
    return redirect(url_for('moviles'))

@app.route('/incidentes/cambiar_estado', methods=['GET', 'POST'])
def cambiar_estado_incidente():
    if request.method == 'POST':
        incidente_id = request.form['incidente_id']
        nuevo_estado = request.form['estado']
        incidente = Incidente.getOne(incidente_id)
        incidente.setState(nuevo_estado)
        movil = Movil.getOne(incidente.movil_id)
        if incidente.estado == 'finalizado':
            movil.setState('disponible')
        
        redirect(url_for('incidentes'))
    return redirect(url_for('incidentes'))

@app.route('/disponibles' , methods = ['GET', 'POST'])
def disponibles():
    cuartel = request.args.get('cuartel', 'Todos', type=str)
    
    if cuartel == 'Todos':
        moviles = Movil.getDisponibles()
    else:
        moviles = Movil.getDisponiblesByCuartel(cuartel)
    
    cuarteles = Movil.getAllCuarteles()

    return render_template('listar_moviles_disponibles.html', moviles=moviles, cuarteles=cuarteles)

@app.route('/incidente', methods = ['GET', 'POST'])
def crear_incidente():
    n_movil = request.args.get('n_movil', None, type=str)

    if n_movil is None:
        return redirect(url_for('disponibles'))
    
    if request.method == 'POST':
        operador = request.form['operador']
        servicio = request.form['servicio']
        tipo_servicio = request.form['tipo_servicio']
        salida = datetime.strptime(request.form['salida'], '%Y-%m-%dT%H:%M')
        llegada = datetime.strptime(request.form['llegada'], '%Y-%m-%dT%H:%M')
        lugar = request.form['lugar']
        observaciones = request.form['observaciones']
        try:
            movil = Movil.getMovilByN_movil(n_movil)
            Incidente.createAndCommit(operador, movil.id, servicio, tipo_servicio, salida, llegada, lugar, observaciones)
            try:
                movil.setState('en uso')
            finally:
                return redirect(url_for('incidentes'))
        except:
            return redirect(url_for('disponibles'))
    return render_template('crear_incidente.html', n_movil=n_movil)


@app.route('/incidentes')
def incidentes():
    incidentes = Incidente.getAll()
    return render_template('listar_incidentes.html', incidentes=incidentes)

with app.app_context():
    db.create_all()
# run the app
if __name__ == '__main__':
    app.run( debug=True, port='3000')
