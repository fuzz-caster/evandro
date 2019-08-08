import pandas as pd
import numpy as np
from flask import request, jsonify
from evandro.db import db_session, Rule, Transaksi
from evandro.core.mamdani import predict
from .blueprint import api_blueprint

def _all_data():
    trans = db_session.query(Transaksi).all()
    as_list = [
        [ tr.id, tr.produksi, tr.penjualan, tr.persediaan, tr.permintaan ]
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

@api_blueprint.route("/mape", methods=["GET"])
def mape():
    all_data_pd_with_id = _all_data()
    all_data_pd = all_data_pd_with_id.iloc[:, :]
    all_data = all_data_pd.to_numpy().tolist()
    total_data = len(all_data)

    # predict function need previous data as numpy.
    all_data_np = all_data_pd.to_numpy()

    # Rules need to be a list.
    all_rules = _all_rules().to_numpy().tolist()
    result_system = [
        predict(x[1:], all_data_np[:, 1:], all_rules)
        for x in all_data
    ]

    print(result_system)

    result_system = np.array([ r['defuzz'] for r in result_system ])
    result_actual = all_data_np[:, 4]
    diffs = np.abs(result_system - result_actual)
    mape = (diffs / result_actual) * 100.0
    mape = mape.sum() / total_data

    original_data = all_data_pd_with_id.to_dict("record")

    result_actual_native = result_actual.tolist()
    result_system_native = result_system.tolist()

    wrapped = [
        {
            "row": r,
            "actual": result_actual_native[idx],
            "system": result_system_native[idx]
        }
        for idx, r in enumerate(original_data)
    ]

    return jsonify({
        "mape": mape,
        "items": wrapped
    })

@api_blueprint.route("/mse", methods=["GET"])
def mse():
    all_data_pd = _all_data()
    all_data = all_data_pd.to_numpy().tolist()

    # predict function need previous data as numpy.
    all_data_np = all_data_pd.to_numpy()

    # Rules need to be a list.
    all_rules = _all_rules().to_numpy().tolist()

    result_system = [
        predict(x, all_data_np, all_rules)
        for x in all_data
    ]

    result_system = np.array([ r['defuzz'] for r in result_system ])
    result_actual = all_data_np[:, 1]
    raised = np.power(result_system - result_actual, 2)
    total_data = len(all_data)
    mse = raised.sum() / (total_data * 1.0)
    return jsonify({
        "mse": mse
    })