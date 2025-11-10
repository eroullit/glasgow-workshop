from flask import Flask
import folium
import json

app = Flask(__name__)

@app.route('/')
def show_glasgow_map():
    # Glasgow coordinates (city center)
    glasgow_coords = [55.8642, -4.2518]
    
    # Create a map centered on Glasgow
    glasgow_map = folium.Map(
        location=glasgow_coords,
        zoom_start=13,
        tiles='OpenStreetMap'
    )
    
    # Add a marker for Glasgow city center
    folium.Marker(
        glasgow_coords,
        popup='Glasgow City Centre',
        tooltip='Glasgow'
    ).add_to(glasgow_map)
    
    # Load and add Tree Preservation Orders
    with open('Tree_Preservation_Orders_(TPOs).geojson', 'r') as f:
        tpo_data = json.load(f)
    
    # Filter out features with null geometries
    tpo_data['features'] = [
        feature for feature in tpo_data['features'] 
        if feature.get('geometry') is not None
    ]
    
    # Add TPO layer to the map
    folium.GeoJson(
        tpo_data,
        name='Tree Preservation Orders',
        style_function=lambda feature: {
            'fillColor': '#228B22',
            'color': '#006400',
            'weight': 2,
            'fillOpacity': 0.4
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['AREANAME', 'EVNUMBER'],
            aliases=['Area Name:', 'EV Number:'],
            localize=True
        )
    ).add_to(glasgow_map)
    
    # Add layer control
    folium.LayerControl().add_to(glasgow_map)
    
    # Return the map as HTML
    return glasgow_map._repr_html_()

if __name__ == '__main__':
    app.run(port=3000, debug=True)
