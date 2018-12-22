from flask import Flask
# from flask_jsonpify import jsonify
# from issueUtil import prettify
from src.analyzers import distributionAnalyzer, pitcherAnalyzer


def pitchValuesByPitcher(pitcher_name, range_size=50):
    pitches, deltas = pitcherAnalyzer.analyzePitcher("/home/george/Documents/mlnReports/mln_master_log_combined.csv", pitcher_name)
    return distributionAnalyzer.groupValuesByRange(pitches, range_size)