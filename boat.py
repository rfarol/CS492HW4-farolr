from flask import Blueprint, request
from google.cloud import datastore
import json
import constants

client = datastore.Client()

bp = Blueprint('boat', __name__, url_prefix='/boat')

@bp.route('', methods=['POST','GET'])
def boat_get_post():
    if request.method == 'POST':
        content = request.get_json()
        new_boat = datastore.entity.Entity(key=client.key(constants.boat))
        new_boat.update({'name': content['name'], 'type': content['type'],
          'length': content['length']})
        client.put(new_boat)
        return str(new_boat.key.id)
    elif request.method == 'GET':
        query = client.query(kind=constants.boat)
        q_limit = int(request.args.get('limit', '2'))
        q_offset = int(request.args.get('offset', '0'))
        l_iterator = query.fetch(limit= q_limit, offset=q_offset)
        pages = l_iterator.pages
        results = list(next(pages))
        if l_iterator.next_page_token:
            next_offset = q_offset + q_limit
            next_url = request.base_url + "?limit=" + str(q_limit) + "&offset=" + str(next_offset)
        else:
            next_url = None
        for e in results:
            e["id"] = e.key.id
        output = {"boat": results}
        if next_url:
            output["next"] = next_url
        return json.dumps(output)
    else:
        return 'Method not recogonized'

@bp.route('/<id>', methods=['PUT','DELETE'])
def boat_put_delete(id):
    if request.method == 'PUT':
        content = request.get_json()
        boat_key = client.key(constants.boat, int(id))
        boat = client.get(key=boat_key)
        boat.update({'name': content['name'], 'type': content['type'],
          'length': content['length']})
        client.put(boat)
        return ('',200)
    elif request.method == 'DELETE':
        key = client.key(constants.boat, int(id))
        client.delete(key)
        return ('',200)
    else:
        return 'Method not recogonized'

@bp.route('/<bid>/load/<lid>', methods=['PUT','DELETE'])
def add_delete_reservation(bid,lid):
    if request.method == 'PUT':
        boat_key = client.key(constants.boat, int(bid))
        boat = client.get(key=boat_key)
        load_key = client.key(constants.load, int(lid))
        load = client.get(key=load_key)
        if 'load' in boat.keys():
            boat['load'].append(load.id)
        else:
            boat['load'] = [load.id]
        client.put(boat)
        return('',200)
    if request.method == 'DELETE':
        boat_key = client.key(constants.boat, int(bid))
        boat = client.get(key=boat_key)
        if 'load' in boat.keys():
            boat['load'].remove(int(lid))
            client.put(boat)
        return('',200)

@bp.route('/<id>/load', methods=['GET'])
def get_load(id):
    boat_key = client.key(constants.boat, int(id))
    boat = client.get(key=boat_key)
    load_list  = []
    if 'load' in boat.keys():
        for lid in boat['load']:
            load_key = client.key(constants.load, int(lid))
            guest_list.append(load_key)
        return json.dumps(client.get_multi(load_list))
    else:
        return json.dumps([])
