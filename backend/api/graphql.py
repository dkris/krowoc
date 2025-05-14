from flask import Blueprint, request, jsonify
from flask_graphql import GraphQLView
from backend.graphql import schema
from loguru import logger

graphql_bp = Blueprint('graphql', __name__)

# Add the GraphQL endpoint
graphql_bp.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True  # Enable GraphiQL interface for development
    )
)

@graphql_bp.route('/graphql/schema', methods=['GET'])
def get_schema():
    """Endpoint to get the GraphQL schema"""
    try:
        schema_str = str(schema)
        return jsonify({
            "status": "success",
            "schema": schema_str
        }), 200
    except Exception as e:
        logger.error(f"Error getting GraphQL schema: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Failed to get GraphQL schema",
            "error": str(e)
        }), 500 