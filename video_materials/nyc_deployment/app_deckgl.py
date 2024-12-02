import geopandas as gpd
from shiny import App, ui, render, reactive
import pandas as pd 
from pathlib import Path
import sys 
import json
from shapely.geometry import mapping
from shapely import wkt
from shapely.geometry import mapping, box, Point
from pyproj import Transformer

WGS = 'EPSG:4326'
PROJ = 'EPSG:2263'

# Constants remain the same
DATA_DIR = Path("data")
deployments = { 
    'Elmhurst, Queens': {
        'coords': (40.738536, -73.887267),
        'video': 'elmhurst_deployment.mp4'  # Placeholder filename
    },
    'Sutton Place, Manhattan': {
        'coords': (40.758890, -73.958457),
        'video': 'sutton_place_deployment.mp4'
    },
    'Herald Square, Manhattan': {
        'coords': (40.748422, -73.988275),
        'video': 'herald_square_deployment.mp4'
    },
    'Jackson Heights, Queens': {
        'coords': (40.747379, -73.889690),
        'video': 'jackson_heights_deployment.mp4'
    }
}

def create_deployment_polygons():
    transformer = Transformer.from_crs(WGS, PROJ, always_xy=True)
    
    deployment_features = []
    for name, info in deployments.items():
        # Convert to local projection
        lat, lon = info['coords']
        x, y = transformer.transform(lon, lat)
        
        # Create 500m x 500m box
        box_geom = box(x - 250, y - 250, x + 250, y + 250)
        
        # Convert back to WGS84
        box_gdf = gpd.GeoDataFrame(geometry=[box_geom], crs=PROJ).to_crs(WGS)
        
        # Create GeoJSON feature
        feature = {
            "type": "Feature",
            "geometry": mapping(box_gdf.geometry.iloc[0]),
            "properties": {
                "name": name,
                "description": f"Deployment location: {name}",
                "id": len(deployment_features),
                "height": 100,
                "video": info['video']
            }
        }
        deployment_features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": deployment_features
    }

# Define the 11 colors from red to green
COLORS = [
    [165, 0, 38],    # Dark red
    [215, 48, 39],   # Red
    [244, 109, 67],  # Light red
    [253, 174, 97],  # Orange-red
    [254, 224, 144], # Light orange
    [255, 255, 191], # Yellow
    [217, 239, 139], # Light yellow-green
    [166, 217, 106], # Light green
    [102, 189, 99],  # Medium green
    [26, 152, 80],   # Green
    [0, 104, 55]     # Dark green
]

app_ui = ui.page_fluid(
    ui.head_content(
        ui.tags.script({"src": "https://unpkg.com/deck.gl@latest/dist.min.js"}),
        ui.tags.script({"src": "https://unpkg.com/maplibre-gl@2.4.0/dist/maplibre-gl.js"}),
        ui.tags.link({"rel": "stylesheet", "href": "https://unpkg.com/maplibre-gl@2.4.0/dist/maplibre-gl.css"}),
        
        ui.tags.style("""
            /* Reset defaults */
            body {
                margin: 0;
                padding: 0;
                overflow: hidden;
            }
            
            /* Make the fluid page take full viewport */
            .container-fluid {
                padding: 0 !important;
                margin: 0 !important;
                height: 100vh !important;
                width: 100vw !important;
                max-width: none !important;
            }

            /* Base styles */
            .container {
                display: flex;
                max-width: none !important;
                width: 100vw;
                height: 100vh;
                margin: 0;
                padding: 0;
                overflow: hidden;
                position: absolute;
                top: 0;
                left: 0;
            }

            .sidebar {
                background-color: white;
                padding: 1rem;
                box-shadow: 2px 0 5px rgba(0,0,0,0.1);
                z-index: 1000;
                width: 400px;
                overflow-y: auto;
                flex-shrink: 0;
            }

            .main-content {
                flex: 1;
                height: 100vh;
                overflow: hidden;
                position: relative;
            }

            #map {
                width: 100% !important;
                height: 100% !important;
                position: absolute;
                top: 0;
                left: 0;
            }

            .maplibregl-map {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
            }

            .legend-container {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                padding: 10px;
                background: #f5f5f5;
                border-radius: 4px;
                margin-top: 1rem;
            }

            .deployment-popup h3 {
                margin: 0 0 10px 0;
                color: #333;
            }

            .deployment-content {
                min-height: 100px;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }

            .maplibregl-popup {
                z-index: 10;
            }

            .maplibregl-popup-content {
                background: none;
                box-shadow: none;
                padding: 0;
                padding: 0; max-width: none !important;

            }

            .video-container {
                margin-top: 10px;
                width: 100%;
                max-width: 1000px;  /* Adjust based on your needs */
                border-radius: 4px;
                overflow: hidden;
                background: #000;
            }

            .deployment-popup {
                background: white;
                border-radius: 8px;
                padding: 15px;
                min-width: 600px;
                max-width: 1200px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }

            #map {
                z-index: 1;
            }

            .maplibregl-canvas {
                z-index: 1;
            }

            .deck-canvas {
                z-index: 2;
            }

            /* Mobile styles */
            @media (max-width: 768px) {
                .container {
                    flex-direction: column-reverse;
                    height: 100vh;
                }

                .sidebar {
                    width: 100%;
                    height: auto;
                    max-height: 40vh;
                    padding: 0.5rem;
                }

                .main-content {
                    height: 60vh;
                }
            }
        """),
        ui.tags.script("""
            let deckgl;
            let mapgl;
            let viewState = {
                latitude: 40.7128,
                longitude: -74.0060,
                zoom: 12,
                pitch: 45,
                bearing: 0,
                maxZoom: 18,
                minZoom: 10,
                transitionDuration: 300,
                transitionInterpolator: new deck.FlyToInterpolator()
            };

            function generateLayers(data, colors) {
                const layers = [];
    
                if (data.cbs) {
                    layers.push(
                        new deck.GeoJsonLayer({
                            id: 'cbs',
                            data: data.cbs,
                            pickable: false,
                            stroked: true,
                            filled: false,
                            lineWidthScale: 2,
                            getLineColor: [0, 0, 0, 255],
                            parameters: {
                                depthTest: false
                            },
                            // Add tiling parameters
                            loadOptions: {
                                fetch: {
                                    maxRequests: 20,
                                    throttleRequests: true
                                }
                            },
                            tileSize: 256,
                            maxZoom: 20,
                            minZoom: 10,
                            extent: [-74.2, 40.4, -73.7, 40.9], // NYC bounds
                            getTileData: ({id, data}) => data,
                            refinementStrategy: 'no-overlap'
                        })
                    );
                }
                
                if (data.sidewalks && colors.length > 0) {
                    layers.push(
                        new deck.GeoJsonLayer({
                            id: 'sidewalks',
                            data: data.sidewalks,
                            pickable: true,
                            stroked: true,
                            filled: true,
                            lineWidthScale: 8,
                            getLineColor: d => colors[Math.floor(d.properties.score * (colors.length - 1))],
                            getFillColor: d => colors[Math.floor(d.properties.score * (colors.length - 1))],
                            updateTriggers: {
                                getLineColor: colors,
                                getFillColor: colors
                            },
                            parameters: {
                                depthTest: false
                            },
                            // Add tiling parameters
                            loadOptions: {
                                fetch: {
                                    maxRequests: 20,
                                    throttleRequests: true
                                }
                            },
                            tileSize: 256,
                            maxZoom: 20,
                            minZoom: 10,
                            extent: [-74.2, 40.4, -73.7, 40.9], // NYC bounds
                            getTileData: ({id, data}) => data,
                            refinementStrategy: 'no-overlap',
                            // Add culling to improve performance
                            _subLayerProps: {
                                'geojson-layer': {
                                    culling: true,
                                    cullDistanceScale: 2
                                }
                            }
                        })
                    );
                }
                    
                    if (data.deployments) {
                        layers.push(
                            new deck.GeoJsonLayer({
                                id: 'deployments',
                                data: data.deployments,
                                pickable: true,
                                stroked: true,
                                filled: true,
                                extruded: true,
                                getElevation: d => d.properties.height,
                                lineWidthScale: 2,
                                getLineColor: [255, 255, 255, 200],
                                getFillColor: [0, 128, 255, 100],
                                material: {
                                    ambient: 0.64,
                                    diffuse: 0.6,
                                    shininess: 32,
                                    specularColor: [51, 51, 51]
                                },
                                parameters: {
                                    depthTest: false
                                },
                                onClick: (info) => {
                                    if (info.object) {
                                        const popup = new maplibregl.Popup({
                                            closeButton: true,
                                            closeOnClick: false,
                                            maxWidth: '400px'
                                        })
                                            .setLngLat(info.coordinate)
                                            .setHTML(`
                                                <div class="deployment-popup">
                                                    <h3>${info.object.properties.name}</h3>
                                                    <div class="deployment-content">
                                                        <p>${info.object.properties.description}</p>
                                                        <div class="video-container">
                                                            <video
                                                                id="video-${info.object.properties.id}"
                                                                controls
                                                                autoplay
                                                                muted
                                                                style="width: 100%; border-radius: 4px;"
                                                            >
                                                                <source src="/videos/${info.object.properties.video}" type="video/mp4">
                                                                Your browser does not support the video tag.
                                                            </video>
                                                        </div>
                                                    </div>
                                                </div>
                                            `)
                                            .addTo(mapgl);

                                        // Auto-pause video when popup closes
                                        popup.on('close', () => {
                                            const video = document.getElementById(`video-${info.object.properties.id}`);
                                            if (video) {
                                                video.pause();
                                            }
                                        });
                                    }
                                }
                            })
                        );
                    }

                    return layers;
                }

                function initDeck(data, colors) {
                    if (!mapgl) {
                        // First initialize with a style that includes labels
                        mapgl = new maplibregl.Map({
                            container: 'map',
                            style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',  // Style with labels
                            center: [viewState.longitude, viewState.latitude],
                            zoom: viewState.zoom,
                            pitch: viewState.pitch,
                            bearing: viewState.bearing,
                            interactive: true
                        });

                        mapgl.on('load', () => {
                            // Store all symbol layers (labels)
                            const style = mapgl.getStyle();
                            const symbolLayers = style.layers.filter(layer => 
                                layer.type === 'symbol'
                            );
                            
                            // Remove all symbol layers temporarily
                            symbolLayers.forEach(layer => {
                                mapgl.removeLayer(layer.id);
                            });

                            // Add deck.gl overlay
                            const deckOverlay = new deck.MapboxOverlay({
                                layers: generateLayers(data, colors),
                                getTooltip: ({object}) => {
                                    if (!object) return null;
                                    if (object.properties.score !== undefined) {
                                        return {
                                            html: `Score: ${(object.properties.score * 100).toFixed(1)}%`,
                                            style: {
                                                backgroundColor: '#fff',
                                                fontSize: '0.8em',
                                                padding: '4px'
                                            }
                                        };
                                    }
                                    return null;
                                }
                            });

                            mapgl.addControl(deckOverlay);
                            deckgl = deckOverlay;

                            // Re-add symbol layers after deck.gl overlay
                            symbolLayers.forEach(layer => {
                                mapgl.addLayer(layer);
                            });

                            mapgl.addControl(new maplibregl.NavigationControl());
                        });
                    } else {
                        if (deckgl) {
                            deckgl.setProps({
                                layers: generateLayers(data, colors)
                            });
                        }
                    }
                }
                // Restore the original flyTo function
                function sequentialFlyTo(longitude, latitude) {
                    if (mapgl) {
                        const center = mapgl.getCenter();
                        
                        // Step 1: Zoom out to level 12
                        mapgl.flyTo({
                            center: [center.lng, center.lat],
                            zoom: 12,
                            duration: 1500,
                            essential: true
                        });

                        // Step 2: Fly to location
                        setTimeout(() => {
                            mapgl.flyTo({
                                center: [longitude, latitude],
                                zoom: 12,
                                duration: 2000,
                                essential: true
                            });

                            // Step 3: Zoom in
                            setTimeout(() => {
                                mapgl.flyTo({
                                    center: [longitude, latitude],
                                    zoom: 16,
                                    duration: 1500,
                                    essential: true
                                });
                            }, 2000);
                        }, 1500);
                    }
                }

                function updateLayers(data, colors) {
                    if (mapgl && !mapgl.loaded()) {
                        mapgl.on('load', () => initDeck(data, colors));
                    } else {
                        initDeck(data, colors);
                    }
                }

                Shiny.addCustomMessageHandler("updateLayers", function(message) {
                    updateLayers(message.data, message.colors);
                });

                Shiny.addCustomMessageHandler("flyTo", function(message) {
                    sequentialFlyTo(message.longitude, message.latitude);
                });
        """)
    ),
    ui.div(
        {"class": "container"},
        ui.div(
            {"class": "sidebar"},
            ui.div(
                {"class": "control-group"},
                ui.h3("THE ROBOTABILITY SCORE", {"style": "margin-bottom: 1rem; font-style: italic;"}),
                ui.p("New York City deployment, September 2024"),
                ui.input_select(
                    "fly_select", 
                    "Fly to Deployment", 
                    choices=list(deployments.keys())
                )
            ),
            ui.div(
                {"class": "control-group"},
                ui.h3("Layers", {"style": "margin-bottom: 2rem;"}),
                ui.input_checkbox_group(
                    "visible_layers",
                    "",
                    choices=["Sidewalk Scores", "Census Block Boundaries", "Deployment Locations"],
                    selected=["Sidewalk Scores", "Census Block Boundaries", "Deployment Locations"]
                )
            ,{"style": "margin-bottom: 2rem;"}
            ),
            ui.div(
                {"class": "control-group"},
                ui.h4("Score Legend"),
                ui.div(
                    {"class": "legend-container"},
                    [
                        ui.div(
                            {"style": f"background-color: rgb({r},{g},{b}); width: 20px; height: 20px; display: inline-block; margin: 2px;"},
                            ""
                        ) for r, g, b in COLORS
                    ]
                ),
                ui.p("Low → High", {"style": "text-align: center;"})
            )
        ),
        ui.div(
            {"class": "main-content"},
            ui.div({"id": "map"})
        )
    )
)

def server(input, output, session):
    data_store = reactive.Value({})
    
    @reactive.effect
    def load_base_data():
        """Load the base data once at startup"""
        if not data_store.get():
            # Load sidewalk data
            score_by_sidewalk = pd.read_csv("score_by_sidewalk.csv")
            score_by_sidewalk = gpd.GeoDataFrame(
                score_by_sidewalk, 
                geometry=score_by_sidewalk['geometry'].apply(wkt.loads), 
                crs=WGS
            ).to_crs(PROJ)
            
            # Simplify geometries based on zoom level
            score_by_sidewalk['geometry'] = score_by_sidewalk['geometry'].simplify(1.0)
            
            # Remove unnecessary columns to reduce payload size
            score_by_sidewalk = score_by_sidewalk[['score', 'geometry']]
            
            # Pre-calculate color indices to avoid client-side computation
            score_by_sidewalk['color_index'] = (score_by_sidewalk['score'] * 10).astype(int).clip(0, 10)
            
            # Load borough data with simplified geometries
            cb_nyc = gpd.read_file(DATA_DIR / "nycb2020_24c/nycb2020.shp").to_crs(WGS)
            boroughs_of_interest = ['Manhattan', 'Queens', 'Brooklyn', 'Bronx', 'Staten Island']
            cbs = cb_nyc[cb_nyc.BoroName.isin(boroughs_of_interest)].to_crs(PROJ)
            cbs['geometry'] = cbs['geometry'].simplify(5.0)
            
            # Store the processed data
            data_store.set({
                'score_by_sidewalk': score_by_sidewalk,
                'cbs': cbs,
                'deployments': create_deployment_polygons()
            })

    @reactive.calc
    def get_visible_layers():
        """Get the currently visible layers based on user selection"""
        data = data_store.get()
        if not data:
            return {}
            
        result = {}
        
        if "Sidewalk Scores" in input.visible_layers():
            sidewalks_gdf = data['score_by_sidewalk'].to_crs(WGS)
            # Convert to binary protocol
            result["sidewalks"] = {
                "type": "FeatureCollection",
                "features": sidewalks_gdf.__geo_interface__["features"],
                "bbox": sidewalks_gdf.total_bounds.tolist()
            }
            
        if "Census Block Boundaries" in input.visible_layers():
            cbs_gdf = data['cbs'].to_crs(WGS)
            result["cbs"] = json.loads(cbs_gdf.to_json())

        if "Deployment Locations" in input.visible_layers():
            result["deployments"] = data['deployments']
            
        return result

    @reactive.effect
    async def update_map():
        """Update the map when visible layers change"""
        layers_data = get_visible_layers()
        await session.send_custom_message(
            "updateLayers",
            {"data": layers_data, "colors": COLORS}
        )

    @reactive.effect
    async def handle_fly_to():
        """Handle flying to selected deployment"""
        selected = input.fly_select()
        if selected in deployments:
            coords = deployments[selected]['coords']  # Now we get the coords tuple from the nested dict
            lat, lon = coords  # Unpack from the coords tuple
            await session.send_custom_message(
                "flyTo",
                {
                    "longitude": lon,
                    "latitude": lat,
                    "zoom": 16
                }
            )

app = App(app_ui, server)