from flask import render_template
from flask_login import current_user, login_required
from app.blueprints.main import bp
from app.services.dashboard_service import DashboardService

@bp.route('/')
@login_required
def index():
    data = DashboardService.get_dashboard_data(current_user)
    return render_template('dashboard.html', **data)
