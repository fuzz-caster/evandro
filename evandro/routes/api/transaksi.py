from .blueprint import api_blueprint
from evandro.db import Transaksi, db_session
from flask import g, request, jsonify, make_response
import pandas as pd
import datetime

@api_blueprint.route("/transaksi", methods=["GET"])
def list_transaksi():
    trans = db_session.query(Transaksi).order_by(Transaksi.tanggal.desc()).all()
    result = [ r.to_dict() for r in trans ]
    return jsonify(result)

@api_blueprint.route("/transaksi/<id>", methods=["GET"])
def find_one_transaksi(id):
    result = db_session.query(Transaksi).filter(Transaksi.id == id).first()
    if result is None:
        return make_response(f"Can't find data with id {id}", 404)
    as_dict = result.to_dict()
    print("---dict---")
    print(as_dict)
    return jsonify(as_dict)

@api_blueprint.route("/transaksi", methods=["POST"])
def create_transaksi():
    content = request.json

    # Get last transaksi by date
    last_trans = db_session.query(Transaksi).order_by(Transaksi.tanggal.desc()).first()
    # Inc by 1 day
    content['tanggal'] = last_trans.tanggal + datetime.timedelta(days=1)
    # content["tanggal"] = datetime.datetime.strptime(content['tanggal'], '%Y-%m-%d')

    n_same_date = db_session.query(Transaksi).filter(Transaksi.tanggal == content["tanggal"]).count()
    if n_same_date > 0:
        return make_response("Duplicate date", 500)

    transaksi = Transaksi.fromdict(content)
    db_session.add(transaksi)
    db_session.commit()

    return jsonify(transaksi.to_dict())

@api_blueprint.route("/transaksi/<id>", methods=["PUT"])
def update_transaksi(id):
    transaksi = db_session.query(Transaksi).filter(Transaksi.id == id).first()

    content = request.json
    content["tanggal"] = datetime.datetime.strptime(content['tanggal'], '%Y-%m-%d')

    transaksi.update(**content)
    db_session.commit()

    return jsonify(transaksi.to_dict())

@api_blueprint.route("/transaksi/<id>", methods=["DELETE"])
def delete_transaksi(id):
    db_session.query(Transaksi).filter(Transaksi.id == id).delete()
    db_session.commit()
    return "OK"

@api_blueprint.route("/last-transaksi")
def last_transaksi():
    last_transaksi = db_session.query(Transaksi).order_by(Transaksi.tanggal.desc()).first()
    return jsonify(last_transaksi.to_dict())
