from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Import models here to ensure tables are created
        import models
        db.create_all()
    app.run(debug=True)
