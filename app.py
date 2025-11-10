from flask import Flask
import folium

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
    
    # Return the map as HTML
    return glasgow_map._repr_html_()

if __name__ == '__main__':
    app.run(port=3000, debug=True)
