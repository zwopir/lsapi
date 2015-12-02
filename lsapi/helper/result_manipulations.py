from flask import url_for
from lsapi.model.defaults import INTEGER_COLUMNS


def downtimes2array(ent):
    new_ent = ent
    try:
        for key in ['downtimes', 'host_downtimes']:
            if key in ent and ent[key]:
                tmparray = []
                for dt_id in ent[key].split(','):
                    tmparray.append({
                                    "uri": url_for('get_downtime', downtime_id=dt_id, _external=True),
                                    "id": int(dt_id)
                    })
                new_ent[key] = tmparray
    except KeyError:
        return ent
    return new_ent


def identity(foo):
    return foo


def make_public_downtime(downtime):
    new_downtime = downtime
    try:
        new_downtime['uri'] = url_for('get_downtime',
                                      downtime_id=downtime['id'],
                                      _external=True)
    except KeyError:
        return downtime
    return new_downtime


def make_public_comment(comment):
    new_comment = {}
    try:
        for field in comment:
            if field == 'id':
                new_comment['uri'] = url_for('get_comment',
                                             comment_id=comment['id'],
                                             _external=True)
            else:
                new_comment[field] = comment[field]
    except KeyError:
        return comment
    return new_comment


def make_public_service(svc):
    new_service = svc
    try:
        new_service['uri'] = url_for('get_service_filtered_by_host_and_service',
                                     host=svc['host_display_name'],
                                     service=svc['display_name'], _external=True)
    except KeyError:
        return svc
    return new_service


def make_public_host(hst):
    new_host = hst
    try:
        new_host['uri'] = url_for('get_host_filtered_by_name',
                              host=hst['display_name'],
                              _external=True)
    except KeyError:
        return hst
    return new_host


def comments2array(ent):
    new_ent = ent
    try:
        if 'comments' in ent and ent['comments']:
            tmparray = []
            for cmt_id in ent['comments'].split(','):
                tmparray.append({
                    "uri": url_for('get_comment', comment_id=cmt_id, _external=True),
                    "id": int(cmt_id)
                })
            new_ent['comments'] = tmparray
    except KeyError:
        return ent
    return new_ent


def cast_fields(ent):
    for field in ent:
        if field in INTEGER_COLUMNS:
            ent[field] = int(ent[field])
    return ent
