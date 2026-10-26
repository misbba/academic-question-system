from flask import Blueprint, jsonify
from models.database import check_db_health

health_bp = Blueprint('health', __name__)

@health_bp.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check API endpoint verifying Flask server status and MySQL database connectivity.
    """
    db_healthy, db_message = check_db_health()
    
    response = {
        "status": "success",
        "message": "Academic Question System API is running",
        "database": {
            "status": "connected" if db_healthy else "disconnected",
            "detail": db_message
        }
    }
    return jsonify(response), 200
