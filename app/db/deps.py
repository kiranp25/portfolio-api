from app.db.session import sessiolocal

def get_db():
    db = sessiolocal()
    try:
        yield db
    finally:
        db.close()
        
