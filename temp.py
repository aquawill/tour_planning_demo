import folium
from math import radians, cos, sin, degrees, atan2, atan, tan, acos
import requests
from folium.plugins import BeautifyIcon, AntPath
import solution
import json
import csv
import random


def get_degree(latA, lonA, latB, lonB):
    radLatA = radians(latA)
    radLonA = radians(lonA)
    radLatB = radians(latB)
    radLonB = radians(lonB)
    dLon = radLonB - radLonA
    y = sin(dLon) * cos(radLatB)
    x = cos(radLatA) * sin(radLatB) - sin(radLatA) * cos(radLatB) * cos(dLon)
    brng = degrees(atan2(y, x))
    brng = (brng + 360) % 360
    return brng


def get_route(ori_lat, ori_lon, dest_lat, dest_lon, route_mode, departure_time):
    route_url = 'https://route.ls.hereapi.com/routing/7.2/calculateroute.json?'
    wp0 = ('{},{}'.format(ori_lat, ori_lon))
    wp1 = ('{},{}'.format(dest_lat, dest_lon))
    route_options = '&mode={}&departure={}&legAttributes=shape'.format(route_mode, departure_time)
    url = route_url + 'apiKey=' + apikey + '&waypoint0=geo!' + wp0 + '&waypoint1=geo!' + wp1 + route_options
    json_result = json.loads(requests.get(url).text)
    routes = json_result['response']['route']
    route_shape = []
    for route in routes:
        legs = route['leg']
        for leg in legs:
            shape = leg['shape']
            point_index = 0
            while point_index < len(shape):
                point = shape[point_index]
                lat = float(point.split(',')[0])
                lon = float(point.split(',')[1])
                if point_index < len(shape) - 1:
                    avg_lat = (float(lat) + float(shape[point_index + 1].split(',')[0])) / 2
                    avg_lon = (float(lon) + float(shape[point_index + 1].split(',')[1])) / 2
                    bearing = get_degree(lat, lon, float(shape[point_index + 1].split(',')[0]), float(shape[point_index + 1].split(',')[1]))
                route_shape.append(([lat, lon], [avg_lat, avg_lon], bearing))
                point_index += 1
    return route_shape


apikey = 'kVpNlN_Zq68gCvCKaZGJA8No9l-9nQfWKls02XySZus' # your HERE location Services API Key

m = folium.Map(
    #     tiles='https://1.base.maps.ls.hereapi.com/maptile/2.1/maptile/newest/normal.day/{z}/{x}/{y}/256/png8?lg=cht&&apiKey=' + apikey,
    location=[23, 121],
    max_zoom=20,
    attr='(c)1987-2018 HERE'
)
folium.Marker([24.970504, 121.2516], icon=BeautifyIcon(icon='home', iconShape='marker', background_color='#000000', text_color='#FFFFFF'), popup='Home').add_to(m)

bounds = []

destinations = 'destinations.csv'
destination_list = open(destinations, encoding='utf-8')
destination_dict_list = csv.DictReader(destination_list)
customer_dict = {}
unreachable_customer_names = []

solution = solution.solution_from_dict(j)

unassigned = solution.unassigned
unassigned_feature_group = folium.map.FeatureGroup(name='Unassigned', overlay=True, control=True, show=True)
icon_color = '#FF0000'
for destination_dict in destination_dict_list:
    customer_dict[destination_dict['customer_id']] = destination_dict['name']
    for unassigned_destination in unassigned:
        job_id = unassigned_destination.job_id
        customer_name = ''
        if destination_dict['customer_id'] == job_id:
            customer_name = destination_dict['name']
            unreachable_customer_names.append(customer_name)
            folium.Marker([destination_dict['latitude'], destination_dict['longitude']], icon=BeautifyIcon(icon='ban', iconShape='marker', background_color=icon_color, border_width=2), popup='{}/{}<br>{}'.format(job_id, customer_name, unassigned_destination.reasons.__getitem__(0).description)).add_to(unassigned_feature_group)
unassigned_feature_group.add_to(m)
print("unreachable customers: ")
print(unreachable_customer_names)

tour_index = 0
while tour_index < len(solution.tours):
    icon_color = '#'
    i = 0
    while i < 6:
        icon_color += hex(random.randint(6, 16))[-1]
        i += 1
    tour = solution.tours.__getitem__(tour_index)
    vehicle_id = tour.vehicle_id
    print("calculating routes for tour: {} / vehicle: {} / {} stops".format(tour_index, vehicle_id, len(tour.stops)))
    feature_group = folium.map.FeatureGroup(name=vehicle_id, overlay=True, control=True, show=True)
    type_id = tour.type_id
    stops = tour.stops
    stop_index = 0
    while stop_index < len(stops):
        stop = stops.__getitem__(stop_index)
        stop_location = stop.location.to_dict()
        stop_time = stop.time
        stop_time_arrival = stop.time.arrival
        stop_time_departure = stop.time.departure
        stop_activities = stop.activities
        for stop_activity in stop_activities:
            job_id = stop_activity.job_id
            customer_name = customer_dict.get(job_id)
            stop_load = stop.load
            if stop_index < len(stops) - 1:
                route_shape = get_route(stop_location['lat'], stop_location['lng'], stops.__getitem__(stop_index + 1).location.to_dict()['lat'], stops.__getitem__(stop_index + 1).location.to_dict()['lng'], 'truck;fastest', stop_time_departure.strftime('%Y-%m-%dT%H:%M:%SZ'))
                if stop_index > 0:
                    folium.Marker([stop_location['lat'], stop_location['lng']], icon=BeautifyIcon(icon='flag', iconShape='marker', background_color=icon_color, border_width=2), popup='Vehicle ID: {}<br>Job ID: {}/{}<br>Arrival：{}<br>Departure：{}'.format(vehicle_id, job_id, customer_name, stop_time_arrival, stop_time_departure)).add_to(feature_group)
                shape_point_index = 0
                bounds.append([stop_location['lat'], stop_location['lng']])
                shape_point_list = []
                while shape_point_index < len(route_shape):
                    shape_point = route_shape[shape_point_index]
                    shape_point_list.append(shape_point[0])
                    shape_point_index += 1
                AntPath(shape_point_list, color=icon_color, weight=4, opacity=1).add_to(feature_group)
            print('{} --> {}/{}'.format(stop_index, job_id, customer_name))
        stop_index += 1
    statistic = tour.statistic
    feature_group.add_to(m)
    tour_index += 1
