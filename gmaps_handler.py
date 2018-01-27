import googlemaps
from datetime import datetime
import json
import re

API_KEY='xxx'

LOCATIONS = {
    'office': "addr1",
    'home': "addr2"
}

class GmapsHandler(object):
    def __init__(self):
        self.client = googlemaps.Client(key=API_KEY)

    def get_route(self, source='', destination='', directions=False):
        if not destination:
            destination = LOCATIONS['office']
        if destination.lower() in LOCATIONS:
            destination = LOCATIONS[destination.lower()]
        if not source:
            source = LOCATIONS['home']
        if source.lower() in LOCATIONS:
            source = LOCATIONS[source.lower()]

        try:
            directions_result = self.client.directions(
                source, destination,alternatives=True,
                departure_time=datetime.now())
        except Exception as e:
            return self._format_result('', '')

        best_duration = 100000000
        best_route = ''
        x = ''
        for route in directions_result:
            duration = route['legs'][0]['duration_in_traffic']
            if duration['value'] < best_duration:
                best_duration = duration['value']
                best_route = route['summary']
                best_time = duration['text']
                steps = route['legs'][0]['steps']
        path = ''
        if 'CA-237' in best_route:
            for step in steps:
                if 'I-880 N' in step['html_instructions']:
                    path = 'I-880 N'
                if 'Zanker' in step['html_instructions']:
                    path = 'Zanker Rd'
        if path != '':
            best_route += ' via '+ path
        if directions:
            inst_list = []
            for step in steps:
                inst_list.append(self._format_instructions(step['html_instructions']))
            return '\n'.join(inst_list)

        return self._format_result(best_route, best_time)

    def _format_instructions(self, inst):
        inst = re.sub('<b>','', inst)
        inst = re.sub('</b>','', inst)
        inst = re.sub('<div style="font-size:0.9em">','\n', inst)
        inst = re.sub('</div>','', inst)
        return inst

    def _format_result(self, route, duration):
        if route:
            response = ('The fastest route is {route}. '
                        'Duration {duration}.')
            response = response.format(route=route, duration=duration)
        else:
            response = "Sorry, I couldn't find a route for your destination."

        return response

# obj = GmapsHandler()
# print obj.get_route(destination='Walmart', directions=True)
