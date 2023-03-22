from flask import render_template, request, redirect, url_for, Blueprint
from datetime import datetime
from bomberman_app.models import Movil, Incidente

app_views = Blueprint('app_views', __name__,
                        template_folder='../views')

@app_views.route('/')
def home():
    return render_template('home.html')

@app_views.route('/movil', methods = ['GET', 'POST'])
def crear_movil():
    if request.method == 'POST':
        n_movil = request.form['n_movil']
        cuartel = request.form['cuartel']
        tipo = request.form['tipo']
        Movil.createAndCommit(n_movil, cuartel, tipo)
        return redirect(url_for('app_views.moviles'))
    return render_template('crear_movil.html')

@app_views.route('/moviles')
def moviles():
    moviles = Movil.getAll()
    return render_template('listar_moviles.html', moviles=moviles)

@app_views.route('/moviles/<int:movil_id>/cambiar_estado', methods=['POST'])
def cambiar_estado(movil_id):
    nuevo_estado = request.form['estado']
    movil = Movil.getOne(movil_id)
    movil.setState(nuevo_estado)
    return redirect(url_for('app_views.moviles'))

@app_views.route('/incidentes/cambiar_estado', methods=['GET', 'POST'])
def cambiar_estado_incidente():
    if request.method == 'POST':
        incidente_id = request.form['incidente_id']
        nuevo_estado = request.form['estado']
        incidente = Incidente.getOne(incidente_id)
        incidente.setState(nuevo_estado)
        movil = Movil.getOne(incidente.movil_id)
        if incidente.estado == 'finalizado':
            movil.setState('disponible')
        
        redirect(url_for('app_views.incidentes'))
    return redirect(url_for('app_views.incidentes'))

@app_views.route('/disponibles' , methods = ['GET', 'POST'])
def disponibles():
    cuartel = request.args.get('cuartel', 'Todos', type=str)
    
    if cuartel == 'Todos':
        moviles = Movil.getDisponibles()
    else:
        moviles = Movil.getDisponiblesByCuartel(cuartel)
    
    cuarteles = Movil.getAllCuarteles()

    return render_template('listar_moviles_disponibles.html', moviles=moviles, cuarteles=cuarteles)

@app_views.route('/incidente', methods = ['GET', 'POST'])
def crear_incidente():
    n_movil = request.args.get('n_movil', None, type=str)

    if n_movil is None:
        return redirect(url_for('app_views.disponibles'))
    
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
                return redirect(url_for('app_views.incidentes'))
        except:
            return redirect(url_for('app_views.disponibles'))
    return render_template('crear_incidente.html', n_movil=n_movil)


@app_views.route('/incidentes')
def incidentes():
    incidentes = Incidente.getAll()
    return render_template('listar_incidentes.html', incidentes=incidentes)