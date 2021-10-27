from flask import Blueprint, request
from google.cloud import datastore
import json
from json2html import *
import constants

client = datastore.Client()

bp = Blueprint('load', __name__, url_prefix='/load')

@bp.route('', methods=['POST','GET'])
def load_get_post():
    if request.method == 'POST':
        content = request.get_json()
        new_load = datastore.entity.Entity(key=client.key(constants.load))
        new_load.update({"volume": content["volume"]})
        client.put(new_load)
        return str(new_load.key.id)
    elif request.method == 'GET':
        query = client.query(kind=constants.load)
        q_limit = int(request.args.get('limit', '2'))
        q_offset = int(request.args.get('offset', '0'))
        g_iterator = query.fetch(limit= q_limit, offset=q_offset)
        pages = g_iterator.pages
        results = list(next(pages))
        if g_iterator.next_page_token:
            next_offset = q_offset + q_limit
            next_url = request.base_url + "?limit=" + str(q_limit) + "&offset=" + str(next_offset)
        else:
            next_url = None
        for e in results:
            e["id"] = e.key.id
        output = {"load": results}
        if next_url:
            output["next"] = next_url
        return json.dumps(output)


@bp.route('/<id>', methods=['PUT','DELETE'])
def load_put_delete(id):
    if request.method == 'PUT':
        content = request.get_json()
        load_key = client.key(constants.load, int(id))
        load = client.get(key=load_key)
        load.update({"volume": content["volume"]})
        client.put(load)
        return ('',200)
    elif request.method == 'DELETE':
        key = client.key(constants.load, int(id))
        client.delete(key)
        return ('',200)
    else:
        return 'Method not recogonized'