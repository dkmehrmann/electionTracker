from flask import Flask, render_template
from data import get_chart_data
import json

application = Flask(__name__)


@application.route('/')
@application.route('/index')
def index():

    chart_data = get_chart_data()
    chart_data = json.dumps(chart_data, indent=2)
    data = {'chart_data': chart_data}

    return render_template("index.html", data=data)


if __name__ == "__main__":

    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
