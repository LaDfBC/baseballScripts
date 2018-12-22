from flask import Flask, request
from flask_jsonpify import jsonify
from pandas import DataFrame

from src.web import PitcherService

app = Flask(__name__)

# Issue-based Requests
@app.route('/pitches/<pitcher_name>')
def getPitches(pitcher_name):
    dfOutput = PitcherService.pitchValuesByPitcher(pitcher_name)
    print(dfOutput.to_dict(orient='records'))

    return dfOutput.to_json(orient='columns')

# Point-based Requests
# api.add_resource(PointService.PointsByIssueNumbers, '/points/issues/<issues>')
# api.add_resource(Poitorvice.PointsBySprintInGeneral, '/points/sprints/<sprints>')
# api.add_resource(PointService.PointsByTeamBySprint '/points/')


if __name__ == '__main__':
    app.run(debug=True)