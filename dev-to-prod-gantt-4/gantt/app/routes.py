from flask import Blueprint, request, jsonify
from .continuous_gantt import ContinuousGantt
from .jira_api import JiraAPI
from .auth import 

routes = Blueprint('routes', __name__)

class Routes:
    """Class to handle routing and processing of requests."""

    # def __init__(self):
    #     self.auth = Auth()

    def process(self):
        """Instantiate and invoke methods from other classes."""
        label = request.args.get('label')
        assignee = request.args.get('assignee')
        level = request.args.get('level')

        # Instantiate JiraAPI and fetch data
        jira_api = JiraAPI(label, assignee, level)
        jira_data = jira_api.fetch_data()

        # Instantiate ContinuousGantt and generate chart
        gantt_chart = ContinuousGantt(jira_data)
        chart_image = gantt_chart.generate()

        return jsonify({"status": "success", "image_data": chart_image})

@routes.route('/process', methods=['GET'])
def process_route():
    """Route to process and generate Gantt chart."""
    routes_instance = Routes()
    return routes_instance.process()