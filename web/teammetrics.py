import sys
sys.path.append('/home/swvist/codes/teammetricsweb/')

from flask import Flask
app = Flask(__name__)

#API
import web.api.views
app.add_url_rule('/api/v<api_version>/<team>/', 'metric_all', web.api.views.metric_all)
app.add_url_rule('/api/v<api_version>/<team>/<metric>/', 'metric',  web.api.views.metric)

#UI Views
import web.ui.views
app.add_url_rule('/', 'index', web.ui.views.index)
app.add_url_rule('/getdata/', 'getdata', web.ui.views.get_data)
app.add_url_rule('/<team>/<metric>/', 'teamdata', web.ui.views.teamdata)


## Handle 404 error
@app.errorhandler(404)
def page_not_found(e):
    return "Page Not Found"

## Handle 500 errors
@app.errorhandler(500)
def server_error(e):
    return "Internal Server Error"

if __name__ == '__main__':
    app.debug = True
    app.run()
