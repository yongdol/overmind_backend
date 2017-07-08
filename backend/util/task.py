# -*- coding:utf-8 -*-

from flask import g
from sqlalchemy import text, create_engine
from datetime import datetime

from backend.util.FacebookAPI import Facebook


# Checks tasks required to purchase the service
def check_service(user_id, service_id):
    query = """
                SELECT req.task_id, name, dtext, is_mandatory, is_done, last_check, message, pre_task_id
                FROM service_task_require AS req
                LEFT JOIN task AS tsk ON req.task_id=tsk.id
                LEFT JOIN task_prerequire AS prq ON req.task_id=prq.task_id
                LEFT JOIN user_task_perform AS pfm ON req.task_id=pfm.task_id AND user_id=:user_id
                WHERE service_id=:service_id
            """
    try:
        result = g.db.execute(text(query), service_id=service_id, user_id=user_id).fetchall()
    except:
        raise Exception('DB Execution Error')

    tasks = dict()
    for r in result:
        if r['task_id'] not in tasks:
            tasks[r['task_id']] = {
                'id': r['task_id'],
                'name': r['name'],
                'description': r['dtext'],
                'is_mandatory': True if r['is_mandatory'] is 1 else False,
                'is_done': True if r['is_done'] is 1 else False,
                'last_check': r['last_check'],
                'message': r['message'] if r['message'] is not None else '내역 없음',
                'prerequsite': []
            }
        if r['pre_task_id'] is not None:
            tasks[r['task_id']]['prerequsite'].append(r['pre_task_id'])

    for t_id in tasks:
        if validation_required(user_id, t_id):
            tasks[r['task_id']]['is_done'], tasks[r['task_id']]['message'] = validate(user_id, t_id)

    return tasks


# Returns list of required tasks
def required_tasks(service_id, mandatory_only=True):
    query = """
                SELECT task_id
                FROM service_task_require
                WHERE service_id=:service_id
            """
    if mandatory_only:
        query += 'AND is_mandatory=1'

    try:
        result = g.db.execute(text(query), service_id=service_id).fetchall()
    except:
        raise Exception('DB Execution Error')

    return [req['task_id'] for req in result] if result is not None else []


# Changes the state of the task
def update_state(user_id, task_id, is_done, message):
    query = """
                INSERT INTO user_task_perform (user_id, task_id, is_done, message, last_check)
                VALUES (:user_id, :task_id, :is_done, :message, :last_check)
                ON DUPLICATE KEY UPDATE is_done=:is_done, message=:message, last_check=:last_check
            """
    try:
        g.db.execute(text(query),
                     user_id=user_id, task_id=task_id, is_done=is_done, message=message, last_check=datetime.utcnow())
    except Exception as e:
        raise Exception('DB Execution Error')


# Checks the task needs validation or not
def validation_required(user_id, task_id):
    # TODO: Make functions
    return False


# Validates the task
def validate(user_id, task_id):
    # TODO: Make validators for every task
    validators = {
        1: val_fb_token
    }

    is_done, message = validators.get(task_id, lambda u_id: (True, u'유효함'))(user_id)
    update_state(user_id, task_id, is_done, message)

    return is_done, message


# Validates all given tasks
def validate_all(user_id, task_ids):
    return {t_id: validate(user_id, t_id)[0] for t_id in task_ids}


# Validates facebook token
def val_fb_token(user_id):
    query = """
                SELECT cred_value
                FROM credential
                WHERE user_id=:user_id AND cred_key='fb_access_token'
            """

    result = g.db.execute(text(query), user_id=user_id).fetchall()

    if len(result) <= 0:
        return False, u'사용자 토큰 정보 없음'

    token = result[0][0]
    fb = Facebook(token)
    if 'error' in fb.get('me'):
        return False, u'토큰이 유효하지 않음'
    else:
        return True, u'토큰 유효함'
