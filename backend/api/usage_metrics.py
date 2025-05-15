from flask import Blueprint, jsonify, request, g
from sqlalchemy import func, distinct, extract, cast, Date
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from ..models.execution import Execution
from ..models.user import User
from ..utils.auth import authenticate
from ..utils.db import get_db

bp = Blueprint('usage_metrics', __name__, url_prefix='/api/metrics')

@bp.route('/summary', methods=['GET'])
@authenticate
def get_usage_summary():
    """Get a summary of usage metrics for the current user."""
    user_id = g.user.id
    db = get_db()
    
    # Get total metrics
    total_metrics = db.query(
        func.count(Execution.id).label('total_executions'),
        func.sum(Execution.input_tokens).label('total_input_tokens'),
        func.sum(Execution.output_tokens).label('total_output_tokens'),
        func.sum(Execution.cost).label('total_cost'),
        func.avg(Execution.execution_time_ms).label('avg_execution_time')
    ).filter(Execution.user_id == user_id).first()
    
    # Get metrics by model
    model_metrics = db.query(
        Execution.model,
        Execution.provider,
        func.count(Execution.id).label('executions'),
        func.sum(Execution.input_tokens).label('input_tokens'),
        func.sum(Execution.output_tokens).label('output_tokens'),
        func.sum(Execution.cost).label('cost')
    ).filter(
        Execution.user_id == user_id
    ).group_by(
        Execution.model, Execution.provider
    ).all()
    
    model_data = [
        {
            'model': metric.model,
            'provider': metric.provider,
            'executions': metric.executions or 0,
            'input_tokens': metric.input_tokens or 0,
            'output_tokens': metric.output_tokens or 0,
            'cost': float(metric.cost or 0)
        } for metric in model_metrics
    ]
    
    return jsonify({
        'summary': {
            'total_executions': total_metrics.total_executions or 0,
            'total_input_tokens': total_metrics.total_input_tokens or 0,
            'total_output_tokens': total_metrics.total_output_tokens or 0,
            'total_cost': float(total_metrics.total_cost or 0),
            'avg_execution_time_ms': float(total_metrics.avg_execution_time or 0)
        },
        'by_model': model_data
    })

@bp.route('/daily', methods=['GET'])
@authenticate
def get_daily_metrics():
    """Get daily usage metrics for the last 30 days."""
    user_id = g.user.id
    db = get_db()
    
    # Get date range from query params or default to last 30 days
    days = request.args.get('days', 30, type=int)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get daily metrics
    daily_metrics = db.query(
        cast(Execution.created_at, Date).label('date'),
        func.count(Execution.id).label('executions'),
        func.sum(Execution.input_tokens).label('input_tokens'),
        func.sum(Execution.output_tokens).label('output_tokens'),
        func.sum(Execution.cost).label('cost')
    ).filter(
        Execution.user_id == user_id,
        Execution.created_at >= start_date,
        Execution.created_at <= end_date
    ).group_by(
        cast(Execution.created_at, Date)
    ).order_by(
        cast(Execution.created_at, Date)
    ).all()
    
    daily_data = [
        {
            'date': metric.date.isoformat(),
            'executions': metric.executions or 0,
            'input_tokens': metric.input_tokens or 0,
            'output_tokens': metric.output_tokens or 0,
            'cost': float(metric.cost or 0)
        } for metric in daily_metrics
    ]
    
    return jsonify({
        'daily_metrics': daily_data
    })

@bp.route('/cost_breakdown', methods=['GET'])
@authenticate
def get_cost_breakdown():
    """Get cost breakdown by provider and model."""
    user_id = g.user.id
    db = get_db()
    
    # Get metrics by provider
    provider_metrics = db.query(
        Execution.provider,
        func.sum(Execution.cost).label('total_cost')
    ).filter(
        Execution.user_id == user_id
    ).group_by(
        Execution.provider
    ).all()
    
    provider_data = [
        {
            'provider': metric.provider,
            'cost': float(metric.total_cost or 0)
        } for metric in provider_metrics
    ]
    
    return jsonify({
        'cost_breakdown': provider_data
    }) 