# from flask_jsonpify import jsonify
# from issueUtil import prettify
from src.analyzers import distributionAnalyzer
from src.reader import pitchFetcher


def pitchValuesByPitcher(pitcher_name, range_size=50):
    pitches, deltas = pitchFetcher.fetchPitchesByPitcherAndLocalFile("/home/george/Documents/mlnReports/mln_master_log_combined.csv", pitcher_name)
    return distributionAnalyzer.groupValuesByRange(pitches, range_size)