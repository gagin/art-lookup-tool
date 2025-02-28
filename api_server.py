#!/usr/bin/env python3
"""
Standalone API server for Vancouver Public Art Status

This provides a REST API for checking status of Vancouver public art objects.
It can be used as an alternative to the direct tool integration with Open WebUI.
"""

import os
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from vancouver_art_status_tools import Tools

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the tools
tools = Tools()

@app.route('/status', methods=['GET'])
def get_status():
    """
    API endpoint to get status of an artwork
    
    Query parameters:
    - q: The name of the artwork to look up
    - details: If 'true', include additional details
    """
    query = request.args.get('q', '')
    details = request.args.get('details', 'false').lower() == 'true'
    
    if not query:
        return jsonify({"error": "No artwork name provided"}), 400
    
    result = tools.get_artwork_status(query, details)
    return jsonify({"result": result})

@app.route('/list', methods=['GET'])
def list_artworks():
    """
    API endpoint to list active artworks
    
    Query parameters:
    - neighborhood: If provided, filter by this neighborhood
    - limit: Maximum number of results to return
    """
    neighborhood = request.args.get('neighborhood', '')
    limit = int(request.args.get('limit', 5))
    
    result = tools.list_active_artworks(neighborhood, limit)
    return jsonify({"result": result})

@app.route('/compare', methods=['GET'])
def compare_artworks():
    """
    API endpoint to compare multiple artworks
    
    Query parameters:
    - q: Comma-separated list of artwork names
    """
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({"error": "No artwork names provided"}), 400
    
    result = tools.compare_artwork_status(query)
    return jsonify({"result": result})

@app.route('/', methods=['GET'])
def home():
    """Homepage with API documentation"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vancouver Public Art Status API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }
            h1, h2, h3 { color: #333; }
            code { background-color: #f4f4f4; padding: 2px 5px; border-radius: 3px; font-family: monospace; }
            pre { background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
            .endpoint { margin-bottom: 30px; border-bottom: 1px solid #eee; padding-bottom: 20px; }
        </style>
    </head>
    <body>
        <h1>Vancouver Public Art Status API</h1>
        <p>This API provides information about the status of public art objects in Vancouver.</p>
        
        <div class="endpoint">
            <h2>1. Get Artwork Status</h2>
            <p>Check the status of a specific artwork:</p>
            <code>GET /status?q=ARTWORK_NAME&details=false</code>
            <h3>Parameters:</h3>
            <ul>
                <li><strong>q</strong>: The name of the artwork to look up</li>
                <li><strong>details</strong>: (optional) Set to 'true' to include more details</li>
            </ul>
            <h3>Example:</h3>
            <pre>GET /status?q=Digital Orca&details=true</pre>
        </div>
        
        <div class="endpoint">
            <h2>2. List Active Artworks</h2>
            <p>List artworks that are currently in place:</p>
            <code>GET /list?neighborhood=AREA&limit=5</code>
            <h3>Parameters:</h3>
            <ul>
                <li><strong>neighborhood</strong>: (optional) Filter by neighborhood</li>
                <li><strong>limit</strong>: (optional) Maximum number of results to return</li>
            </ul>
            <h3>Example:</h3>
            <pre>GET /list?neighborhood=Stanley Park&limit=10</pre>
        </div>
        
        <div class="endpoint">
            <h2>3. Compare Artworks</h2>
            <p>Compare the status of multiple artworks:</p>
            <code>GET /compare?q=ARTWORK1,ARTWORK2,ARTWORK3</code>
            <h3>Parameters:</h3>
            <ul>
                <li><strong>q</strong>: Comma-separated list of artwork names to compare</li>
            </ul>
            <h3>Example:</h3>
            <pre>GET /compare?q=Digital Orca,Girl in Wetsuit,The Drop</pre>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Server starting on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port)