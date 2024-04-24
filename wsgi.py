from app import app, db
from app.models import Projects

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Projects': Projects}

# для целей отладки, потом убрать
from app.report import reports_in_xl 

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
