import pandas as pd
from flask import request, jsonify
from evandro.db import db_session, Rule, Transaksi
from evandro.core.mamdani import predict
from .blueprint import api_blueprint

def _all_data():
    trans = db_session.query(Transaksi).all()
    as_list = [
        [ tr.produksi, tr.penjualan, tr.persediaan, tr.permintaan ]
        for tr in trans
    ]
    return pd.DataFrame(as_list)

def _all_rules():
    rules = db_session.query(Rule).all()
    as_list = [
        [r.produksi, r.penjualan, r.persediaan, r.permintaan]
        for r in rules
    ]
    return pd.DataFrame(as_list)

@api_blueprint.route("/mamdani", methods=["POST"])
def mamdani_classification():
    content = request.json
    x_test = content["payload"]
    all_data = _all_data()
    all_rules = _all_rules()
    all_rules = all_rules.to_numpy().tolist()
    Xs = all_data.to_numpy()
    result = predict(x_test, Xs, all_rules)
    return jsonify(result)
