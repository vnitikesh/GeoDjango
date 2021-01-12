from django.shortcuts import render
from .models import Measurement
from .forms import MeasurementModelForm
from geopy.geocoders import Nominatim
from .utils import get_geo, get_center_coordinates, get_zoom, get_client_ip_address
from geopy.distance import geodesic
import folium



# Create your views here.


def calculate_distance_view(request):
    distance = None
    destination = None
    form_data = None
    obj = Measurement.objects.all()
    #Getting the form instance
    form = MeasurementModelForm(request.POST or None)
    geolocator = Nominatim(user_agent = "MainApp")
    #Getting the ip address of client
    ip_ = get_client_ip_address(request)
    print(ip_)
    ip = '72.14.207.99' #getting this from geoip dir (maxmind.com), ip addres of google's one of the server
    #Getting the geo location from utils.py including country, city, latitude, longitude
    country, city, lat, lon = get_geo(ip)

    location = geolocator.geocode(city)

    #Getting the source ip coordinates
    l_lat = lat
    l_lon = lon
    pointA = (l_lat, l_lon)
    #Initializing folium map(We can set the height and width of map by setting the height and width attribute)
    m = folium.Map(location = get_center_coordinates(l_lat, l_lon), zoom_start = 10)
    #location marker using folium.Marker and add it to map using add_to()
    folium.Marker([l_lat, l_lon], tooltip = 'click here to know more', popup = location,
                    icon = folium.Icon(color='red')).add_to(m)
    # if form is valid
    if(form.is_valid()):
        # Instantiate the form and create the copy of data using commit = False
        instance = form.save(commit = False)
        destination_ = form.cleaned_data.get('destination')#Getting the form data(destination)
        try:

            destination = geolocator.geocode(destination_)#A geolocator instance is created from which address and coordinates can be grab(obj.address, obj.latitude, obj.longitude)

            #Getting the destination ip coordinates
            d_lat = destination.latitude
            d_long = destination.longitude

            pointB = (d_lat, d_long)

            #Getting the distance between pointA and pointB in kms using geodesic
            distance = round(geodesic(pointA, pointB).km, 2)
            instance.location = location#From line 24
            instance.distance = distance#From line 48
            #Saving and persisting the instance in the database
            instance.save()

            #Initializing folium map
            m = folium.Map(location = get_center_coordinates(l_lat, l_lon, d_lat, d_long), zoom_start = get_zoom(distance))
            #location marker
            folium.Marker([l_lat, l_lon], tooltip = 'click here to know more', popup = city,
                            icon = folium.Icon(color='red')).add_to(m)

            #Destination marker
            folium.Marker([d_lat, d_long], tooltip = 'click here to know more', popup = destination,
                            icon = folium.Icon(color='purple')).add_to(m)

            # Draw a line
            line = folium.PolyLine([pointA, pointB], weight = 8, color = 'blue', tooltip = distance)
            #Adding a line between two points using add_child()
            m.add_child(line)
        except:
            form_data = "Invalid data"

    #HTML representation of the map
    m = m._repr_html_()

    return render(request, 'MainApp/index.html', {'distance': distance, 'form': form, 'map': m, 'destination': destination, 'form_data' : form_data})
