from flask import render_template
from . import admin


@admin.route('')
@admin.route('/')
def hello_admin():
    return render_template("admin/hello_admin.html")