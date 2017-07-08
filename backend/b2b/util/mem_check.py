# -*- coding:utf-8 -*-
from flask import g
from sqlalchemy import text


def member_type_check(user_id):
    memtype_query = text("SELECT member_type FROM firm_info inner join user on user.firm_id=firm_info.firm_id where id=:user_id")
    member_type = g.db.execute(memtype_query, user_id=user_id).fetchone()[0]

    return member_type
