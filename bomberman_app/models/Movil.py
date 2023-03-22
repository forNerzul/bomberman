from config.db_instance import db

class Movil(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    n_movil = db.Column(db.String(80), unique=True, nullable=False)
    cuartel = db.Column(db.String(80), unique=False, nullable=False)
    tipo = db.Column(db.String(80), unique=False, nullable=False)
    estado = db.Column(db.String(80), unique=False, default='disponible', nullable=True)

    @classmethod
    def getAll(cls):
        return cls.query.all()
    
    @classmethod
    def getOne(cls,id):
        return cls.query.get_or_404(id)
    
    @classmethod
    def getDisponibles(cls):
        return cls.query.filter_by(estado='disponible').all()
    
    @classmethod
    def getDisponiblesByCuartel(cls, cuartel):
        return cls.query.filter_by(estado='disponible').filter(Movil.cuartel == cuartel).all()
    
    @classmethod
    def getAllCuarteles(cls):
        cuarteles = ['Todos']
        moviles = cls.query.filter_by(estado='disponible').all()
        for movil in moviles:
            if movil.cuartel not in cuarteles:
                cuarteles.append(movil.cuartel)
        return cuarteles
    
    @classmethod
    def createAndCommit(cls, n_movil, cuartel, tipo):
        movil = cls(n_movil=n_movil, cuartel=cuartel, tipo=tipo)
        db.session.add(movil)
        db.session.commit()

    @classmethod
    def getMovilByN_movil(cls, n_movil):
        movil = cls.query.filter_by(n_movil=n_movil).first()
        return movil
    
    def setState(self, state):
        self.estado = state
        db.session.commit()