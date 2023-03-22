from config.db_instance import db

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

    @classmethod
    def getAll(cls):
        return cls.query.all()
    
    @classmethod
    def getOne(cls, id):
        return cls.query.get_or_404(id)
    
    @classmethod
    def createAndCommit(cls, operador, movil_id, servicio, tipo_servicio, salida, llegada, lugar, observaciones):
        incidente = cls(operador=operador, movil_id=movil_id, servicio=servicio, tipo_servicio=tipo_servicio, salida=salida, llegada=llegada, lugar=lugar, observaciones=observaciones)
        db.session.add(incidente)
        db.session.commit()
        
    def setState(self, state):
        self.estado = state
        db.session.commit()