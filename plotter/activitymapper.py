import math, os
import dotenv as dot
import importlib.resources as pkg_resources

dot.load_dotenv()
API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
marker = ''
with pkg_resources.path('resources', 'marker.png') as p:
    marker = p

class Map(object):
 
    def __init__(self):
        self._points = []
 
    def add_point(self, coordinates):
        if not ((math.isnan(coordinates[0])) or (math.isnan(coordinates[1])) or (math.isnan(coordinates[2]))):
            self._points.append(coordinates)

    @staticmethod
    def _lat_rad(lat):
        # Helper function for _get_zoom()
        sinus = math.sin(math.radians(lat + math.pi / 180))
        rad_2 = math.log((1 + sinus) / (1 - sinus)) / 2
        return max(min(rad_2, math.pi), -math.pi) / 2
 
    def _get_zoom(self, map_height_pix=900, map_width_pix=1900, zoom_max=21):
        """
        Algorithm to derive zoom from the activity route. For details please see
         - https://developers.google.com/maps/documentation/javascript/maptypes#WorldCoordinates
         - http://stackoverflow.com/questions/6048975/google-maps-v3-how-to-calculate-the-zoom-level-for-a-given-bounds
        :param zoom_max: maximal zoom level based on Google Map API
        :return:
        """
 
        # at zoom level 0 the entire world can be displayed in an area that is 256 x 256 pixels
        world_heigth_pix = 256
        world_width_pix = 256
 
        # get boundaries of the activity route
        max_lat = max(x[0] for x in self._points)
        min_lat = min(x[0] for x in self._points)
        max_lon = max(x[1] for x in self._points)
        min_lon = min(x[1] for x in self._points)
 
        # calculate longitude fraction
        diff_lon = max_lon - min_lon
        if diff_lon < 0:
            fraction_lon = (diff_lon + 360) / 360
        else:
            fraction_lon = diff_lon / 360
 
        # calculate latitude fraction
        fraction_lat = (self._lat_rad(max_lat) - self._lat_rad(min_lat)) / math.pi
 
        # get zoom for both latitude and longitude
        zoom_lat = math.floor(math.log(map_height_pix / world_heigth_pix / fraction_lat) / math.log(2))
        zoom_lon = math.floor(math.log(map_width_pix / world_width_pix / fraction_lon) / math.log(2))
        return min(zoom_lat, zoom_lon, zoom_max)

    def __str__(self):
        """
        A Python wrapper around Google Map Api v3; see
         - https://developers.google.com/maps/documentation/javascript/
         - https://developers.google.com/maps/documentation/javascript/examples/polyline-simple
         - http://stackoverflow.com/questions/22342097/is-it-possible-to-create-a-google-map-from-python
        :return: string to be stored as html and opened in a web browser
        """
        # center of the activity route
        center_lat = (max((x[0] for x in self._points)) + min((x[0] for x in self._points))) / 2
        center_lon = (max((x[1] for x in self._points)) + min((x[1] for x in self._points))) / 2
 
        # get zoom needed for the route
        zoom = self._get_zoom()
 
        # string with points for the google.maps.Polyline/heatmap
        heatmap_data = ',\n'.join(
            [f'{{"lat": {x[0]}, "long": {x[1]}, "weight": {x[2]}}}' for x in self._points])

        return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Heatmaps</title>
                <style>
                /* Always set the map height explicitly to define the size of the div
                * element that contains the map. */
                #map {{
                    height: 100%;
                }}
                /* Optional: Makes the sample page fill the window. */
                html, body {{
                    height: 100%;
                    margin: 0;
                    padding: 0;
                }}
                #floating-panel {{
                    background-color: 'transparent';
                    left: 1%;
                    padding: 0px;
                    position: absolute;
                    top: 60px;
                    z-index: 5;
                }}
                #floating-panel2 {{
                    background-color: #fff;
                    left: 1%;
                    padding: 0px;
                    position: absolute;
                    top: 90px;
                    z-index: 5;
                }}
                #floating-panel3 {{
                    background-color: 'transparent';
                    left: 1%;
                    padding: 0px;
                    position: absolute;
                    top: 110px;
                    z-index: 5;
                }}
                </style>
            </head>

            <body>
                <div id="floating-panel">
                <button onclick="toggleHeatmap()">Toggle HR-Heatmap/Route</button>
                <button onclick="changeGradient(gradient)">Change gradient</button>
                </div>

                <div class="group">
                    <div id="floating-panel2">
                    <div class="subject">Radius: <span id=radiusNum>5</span></div>
                    </div>
                    <div id="floating-panel3">
                    <button onclick="changeRadius(true)">Up</button>
                    <button onclick="changeRadius(false)">Down</button>
                    </div>
                </div>
                <div id="map"></div>
                <script>

                // This example requires the Visualization library. Include the libraries=visualization
                // parameter when you first load the API. For example:
                // <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=visualization">

                var map, heatmap, activity_route, gradient, marker;
                var heatmap_data = [{heatmap_data}];

                function initMap() {{
                    map = new google.maps.Map(document.getElementById('map'), {{
                        zoom: {zoom},
                        center: new google.maps.LatLng({center_lat}, {center_lon}),
                        mapTypeId: 'terrain'
                    }});
                        
                    gradient = [
                        'rgba(0, 255, 255, 0)',
                        'rgba(0, 255, 255, 1)',
                        'rgba(0, 191, 255, 1)',
                        'rgba(0, 127, 255, 1)',
                        'rgba(0, 63, 255, 1)',
                        'rgba(0, 0, 255, 1)',
                        'rgba(0, 0, 223, 1)',
                        'rgba(0, 0, 191, 1)',
                        'rgba(0, 0, 159, 1)',
                        'rgba(0, 0, 127, 1)',
                        'rgba(63, 0, 91, 1)',
                        'rgba(127, 0, 63, 1)',
                        'rgba(191, 0, 31, 1)',
                        'rgba(255, 0, 0, 1)'
                    ]

                    createMarkers()

                    activity_route = new google.maps.Polyline({{
                        path: getCoordinates(),
                        geodesic: true,
                        strokeColor: '#FF0000',
                        strokeOpacity: 1.0,
                        strokeWeight: 2
                        }});

                    heatmap = new google.maps.visualization.HeatmapLayer({{
                        dissipating: true,
                        data: getPoints(),
                        map: map,
                        radius: 5,
                        gradient: gradient
                        }});
                }};

                function toggleHeatmap() {{
                    heatmap.setMap(heatmap.getMap() ? null : map);
                    activity_route.setMap(activity_route.getMap() ? null : map)
                }};

                function changeGradient(gradient) {{
                    heatmap.set('gradient', heatmap.get('gradient') ? null : gradient);
                }};

                function changeRadius(bool) {{
                    const step = 1, min = 1, max = 20;
                    let current = heatmap.get('radius');
                    let newValue = toggleUpDown(bool, current, step, min, max);

                    heatmap.set('radius', newValue);
                    document.getElementById("radiusNum").innerText = newValue;
                }};

                function toggleUpDown(bool, current, step, min, max){{
                    if (bool && current >= max) return current;
                    if (!bool && current <= min) return current;

                    if (bool) return current + step;
                    return current - step;
                }};

                function getCoordinates() {{
                    str = JSON.stringify(heatmap_data);
                    loc = JSON.parse(str);
                    var arr = [];
                    for (i in loc){{
                        arr.push({{lat: loc[i]["lat"],lng: loc[i]["long"]}});
                    }};
                    console.log(arr)
                    return arr;
                }};

                // Heatmap data
                function getPoints() {{
                    str = JSON.stringify(heatmap_data);
                    loc = JSON.parse(str);
                    var arr = [];
                    for (i in loc){{
                        arr.push({{location: new google.maps.LatLng(loc[i]["lat"],loc[i]["long"]), weight: loc[i]["weight"]}});
                    }};
                    return arr;
                }};

                function createMarkers() {{
                    str = JSON.stringify(heatmap_data);
                    loc = JSON.parse(str);
                    var image = 'https://developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png';

                    for (i in loc) {{
                        var contentstring = 'Heart rate: ' + loc[i]["weight"]
                        var infowindow = new google.maps.InfoWindow({{content: contentstring}})
                        if (i == 0) {{
                            marker = new google.maps.Marker({{
                            position: new google.maps.LatLng(loc[i]["lat"], loc[i]["long"]),
                            map: map,
                            visible: true
                            }});
                        }};
                        if (i == loc.length - 1) {{
                            marker = new google.maps.Marker({{
                            position: new google.maps.LatLng(loc[i]["lat"], loc[i]["long"]),
                            map: map,
                            visible: true,
                            icon: image
                            }});
                        }};
                         marker = new google.maps.Marker({{
                            position: new google.maps.LatLng(loc[i]["lat"], loc[i]["long"]),
                            map: map,
                            visible: true,
                            icon: '{marker}'
                            }});

                        (function(marker,infowindow) {{
                            google.maps.event.addListener(marker,'mouseover', function() {{
                            infowindow.open(map, marker);
                            }});   
                        }})(marker,infowindow);

                        (function(marker, infowindow) {{
                            google.maps.event.addListener(marker, 'mouseout', function() {{
                            infowindow.close();
                            }});
                        }})(marker, infowindow)
                    }};
                }}
                </script>
                <script async defer
                    src="https://maps.googleapis.com/maps/api/js?key={API_KEY}&libraries=visualization&callback=initMap">
                </script>
            </body>
            </html>        
        """