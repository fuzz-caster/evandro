from evandro.db import db_session, Rule, rule_is_unique
from .blueprint import api_blueprint
from flask import g, request, jsonify, make_response
import pandas as pd

@api_blueprint.route("/rules", methods=["POST"])
def rule_create():
    content = request.json
    rule = Rule.fromdict(content)
    r_tuple = rule.to_tuple()
    if (not rule_is_unique(r_tuple)):
        return make_response("Rule is not unique", 500)
    db_session.add(rule)
    db_session.commit()
    return jsonify(rule.to_dict())

@api_blueprint.route("/rules", methods=["GET"])
def rule_find():
    result = db_session.query(Rule).all()
    rule_series = pd.Series( [ r.permintaan for r in result ] )
    rule_counts = rule_series.value_counts()

    total_rules = len(result)
    _0 = int( rule_counts[0] )
    _1 = int( rule_counts[1] )
    _2 = int( rule_counts[2] )

    counts = [total_rules, _0, _1, _2]
    items = [ r.to_dict() for r in result ]

    result = {
        "counts": counts,
        "items": items
    }

    return jsonify(result)

@api_blueprint.route("/rules/<id>", methods=["GET"])
def rule_find_one(id):
    db_session = g.get("db_session")
    result = db_session.query(Rule).filter(Rule.id == id).first()
    if result is None:
        return make_response(f"Can't find data with id {id}", 404)
    return jsonify(result.to_dict())

@api_blueprint.route("/rules/<id>", methods=["PUT"])
def rule_update(id):
    rule = db_session.query(Rule).filter(Rule.id == id).first()

    if rule is None:
        return make_response(f"Can't find data with id {id}", 404)

    content = request.json
    rule = Rule.fromdict(content)
    db_session.add(rule)
    db_session.commit()
    return jsonify(rule.to_dict())

@api_blueprint.route("/rules/<id>", methods=["DELETE"])
def rule_delete(id):
    db_session.query(Rule).filter(Rule.id == id).delete()
    db_session.commit()
    return "OK"
