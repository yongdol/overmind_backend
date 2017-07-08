# -*- coding: utf-8 -*-


def make_job_info(vpc_ip='172.31.38.134', vpn_ip=None, acc_type='card', cred_acc_no=None, cred_user_id=None,
                  cred_user_pw=None, ded_subsc=None, disp_name=u'\ube44\uc528\uce74\ub4dc', dsource_id=6,
                  instance_id='i-0ba239e83b3f0da12', is_free=True, is_scraper=True, job_id=None, last_crawl=None,
                  mod_name='BCCard', plan='onetime', platform='aws', scraper_id=None, status=None, subsc_id=None,
                  subsc_status=None, user_id=None):
    job_info = {
        "VPC_IP": vpc_ip,
        "VPN_IP": vpn_ip,
        "acc_type": acc_type,
        "creds": {
            "cred_acc_no": cred_acc_no,
            "cred_user_id": cred_user_id,
            "cred_user_pw": cred_user_pw
        },
        "ded_subsc": ded_subsc,
        "disp_name": disp_name,
        "dsource_id": dsource_id,
        "instance_id": instance_id,
        "is_free": is_free,
        "is_scraper": is_scraper,
        "job_id": job_id,
        "last_crawl": last_crawl,
        "mod_name": mod_name,
        "plan": plan,
        "platform": platform,
        "scraper_id": scraper_id,
        "status": status,
        "subsc_id": subsc_id,
        "subsc_status": subsc_status,
        "user_id": user_id
    }

    return job_info
