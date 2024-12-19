from flask import Flask, render_template

def handle_dashboard():
    return render_template('dashboard.html')