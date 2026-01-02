

from flask import Flask, jsonify
from flask_cors import CORS
import threading
import os
from datetime import datetime

app = Flask(__name__)

ALLOWED_ORIGINS = [
    "http://localhost:3000",  
    "http://127.0.0.1:3000",   
]

env_origins = os.environ.get('ALLOWED_CORS_ORIGINS', '')
if env_origins:
    ALLOWED_ORIGINS.extend([origin.strip() for origin in env_origins.split(',') if origin.strip()])

CORS(app, origins=ALLOWED_ORIGINS)  


running_pipelines = {}


def run_apollo_pipeline():
    """Execute Apollo pipeline"""
    try:
        from pipeline.pipeline_importing import run_apollo_pipeline
        run_apollo_pipeline()
        running_pipelines['apollo']['status'] = 'completed'
        running_pipelines['apollo']['completed_at'] = datetime.now().isoformat()
    except Exception as e:
        running_pipelines['apollo']['status'] = 'failed'
        running_pipelines['apollo']['error'] = str(e)
        running_pipelines['apollo']['completed_at'] = datetime.now().isoformat()


def run_googlemaps_pipeline():
    """Execute Google Maps pipeline"""
    try:
        from pipeline.pipeline_googlemaps import run_googlemaps_pipeline
        run_googlemaps_pipeline()
        running_pipelines['googlemaps']['status'] = 'completed'
        running_pipelines['googlemaps']['completed_at'] = datetime.now().isoformat()
    except Exception as e:
        running_pipelines['googlemaps']['status'] = 'failed'
        running_pipelines['googlemaps']['error'] = str(e)
        running_pipelines['googlemaps']['completed_at'] = datetime.now().isoformat()


def run_hubspot_pipeline():
    """Execute HubSpot pipeline"""
    try:
        from pipeline.pipeline_hubspot import run_hubspot_pipeline
        run_hubspot_pipeline()
        running_pipelines['hubspot']['status'] = 'completed'
        running_pipelines['hubspot']['completed_at'] = datetime.now().isoformat()
    except Exception as e:
        running_pipelines['hubspot']['status'] = 'failed'
        running_pipelines['hubspot']['error'] = str(e)
        running_pipelines['hubspot']['completed_at'] = datetime.now().isoformat()


@app.route('/')
def index():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'endpoints': {
            '/apollo': 'Run Apollo lead generation pipeline',
            '/googlemaps': 'Run Google Maps scraper pipeline',
            '/hubspot': 'Run HubSpot leads pipeline',
            '/status/<pipeline>': 'Check status of a running pipeline',
            '/status': 'Check status of all pipelines'
        }
    })


@app.route('/apollo', methods=['POST', 'GET'])
def start_apollo_pipeline():
    """Run Apollo lead generation pipeline"""
    pipeline_name = 'apollo'
    
    if pipeline_name in running_pipelines and running_pipelines[pipeline_name]['status'] == 'running':
        return jsonify({
            'status': 'already_running',
            'message': 'Apollo pipeline is already running',
            'started_at': running_pipelines[pipeline_name]['started_at']
        }), 409
    
    running_pipelines[pipeline_name] = {
        'status': 'running',
        'started_at': datetime.now().isoformat(),
        'pipeline': 'apollo'
    }
    
    thread = threading.Thread(target=run_apollo_pipeline, daemon=True)
    thread.start()
    
    return jsonify({
        'status': 'started',
        'message': 'Apollo pipeline started successfully',
        'pipeline': 'apollo',
        'started_at': running_pipelines[pipeline_name]['started_at']
    }), 202


@app.route('/googlemaps', methods=['POST', 'GET'])
def start_googlemaps_pipeline():
    """Run Google Maps scraper pipeline"""
    pipeline_name = 'googlemaps'
    
    if pipeline_name in running_pipelines and running_pipelines[pipeline_name]['status'] == 'running':
        return jsonify({
            'status': 'already_running',
            'message': 'Google Maps pipeline is already running',
            'started_at': running_pipelines[pipeline_name]['started_at']
        }), 409
    
    running_pipelines[pipeline_name] = {
        'status': 'running',
        'started_at': datetime.now().isoformat(),
        'pipeline': 'googlemaps'
    }
    
    thread = threading.Thread(target=run_googlemaps_pipeline, daemon=True)
    thread.start()
    
    return jsonify({
        'status': 'started',
        'message': 'Google Maps pipeline started successfully',
        'pipeline': 'googlemaps',
        'started_at': running_pipelines[pipeline_name]['started_at']
    }), 202


@app.route('/hubspot', methods=['POST', 'GET'])
def start_hubspot_pipeline():
    """Run HubSpot leads pipeline"""
    pipeline_name = 'hubspot'
    
    if pipeline_name in running_pipelines and running_pipelines[pipeline_name]['status'] == 'running':
        return jsonify({
            'status': 'already_running',
            'message': 'HubSpot pipeline is already running',
            'started_at': running_pipelines[pipeline_name]['started_at']
        }), 409
    
    running_pipelines[pipeline_name] = {
        'status': 'running',
        'started_at': datetime.now().isoformat(),
        'pipeline': 'hubspot'
    }
    
    thread = threading.Thread(target=run_hubspot_pipeline, daemon=True)
    thread.start()
    
    return jsonify({
        'status': 'started',
        'message': 'HubSpot pipeline started successfully',
        'pipeline': 'hubspot',
        'started_at': running_pipelines[pipeline_name]['started_at']
    }), 202


@app.route('/status/<pipeline_name>', methods=['GET'])
def get_pipeline_status(pipeline_name):
    """Get status of a pipeline"""
    if pipeline_name not in running_pipelines:
        return jsonify({
            'status': 'not_found',
            'message': f'Pipeline {pipeline_name} not found'
        }), 404
    
    pipeline_info = running_pipelines[pipeline_name].copy()
    response = {
        'pipeline': pipeline_info.get('pipeline', pipeline_name),
        'status': pipeline_info.get('status', 'unknown'),
        'started_at': pipeline_info.get('started_at'),
        'completed_at': pipeline_info.get('completed_at'),
    }
    
    if pipeline_info.get('status') in ['completed', 'failed', 'error']:
        if pipeline_info.get('error'):
            response['error'] = pipeline_info.get('error')[:500]
    
    return jsonify(response), 200


@app.route('/status', methods=['GET'])
def get_all_status():
    """Get status of all pipelines"""
    statuses = {}
    for name, info in running_pipelines.items():
        statuses[name] = {
            'status': info.get('status', 'unknown'),
            'started_at': info.get('started_at'),
            'completed_at': info.get('completed_at'),
        }
    return jsonify(statuses), 200


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("Starting Flask server...")
    print("Available endpoints:")
    print("  GET/POST /apollo - Run Apollo pipeline")
    print("  GET/POST /googlemaps - Run Google Maps pipeline")
    print("  GET/POST /hubspot - Run HubSpot pipeline")
    print("  GET /status/<pipeline> - Check pipeline status")
    print("  GET /status - Check all pipeline statuses")
    print(f"\nServer running on port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
