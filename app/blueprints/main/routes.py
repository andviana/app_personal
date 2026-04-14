from flask import render_template
from app.blueprints.main import bp
from app.services.dashboard_service import DashboardService

@bp.route('/')
def index():
    data = DashboardService.get_dashboard_data()
    return render_template('dashboard.html', **data)
