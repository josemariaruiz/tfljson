import requests

from time import time
import xml.etree.ElementTree as et

from django.shortcuts import render
from django.http import JsonResponse


UPDATE_URL = "http://cloud.tfl.gov.uk/TrackerNet/LineStatus"
XML_NS = "{http://webservices.lul.co.uk/}"



class Line(object):
    def __init__(self):

        self.id = None
        self.name = None
        self.status_code = None
        self.status_details = None
        self.css_class = None
        self.description = None
        self.is_active = None


class Status(object):
    """
    Line Status connection object
    """
    def __init__(self):
        self.update_url = UPDATE_URL
        self.xmlns = XML_NS
        self.lines = {}
        self.last_update = 0
        self.last_request = None
        self.update_time = 30  # TfL asks for 30 seconds between requests

    def update_status(self):
        if (time() - self.last_update) > self.update_time:
            self.last_request = requests.get(self.update_url)
            self.last_update = time()

        root = et.fromstring(self.last_request.content)
        for child in root:
            line = Line()
            line.id = child.find(self.xmlns + 'Line').get('ID')
            line.name = child.find(self.xmlns + 'Line').get('Name')
            line.status_code = child.find(self.xmlns + 'Status').get('ID')
            line.status_details = child.get('StatusDetails')
            line.css_class = child.find(self.xmlns + 'Status').get('CssClass')
            line.description = child.find(self.xmlns + 'Status').get('Description')
            line.is_active = child.find(self.xmlns + 'Status').get('IsActive')
            self.lines[line.name] = line

    def get_status(self, line_code):
        self.update_status()
        if line_code in self.lines:
            return self.lines[line_code]
        else:
            return None

    def list_lines(self):
        self.update_status()
        return self.lines.keys()



def index(request):
    return render(request, 'index.jade')


def status(request):
    current_status = Status()

    # Get a list of tube lines
    lines = current_status.list_lines()

    # Loop through the lines and print the status of each one
    data = {}

    for line in lines:
        data[line] = current_status.get_status(line).description

    return JsonResponse(data)
