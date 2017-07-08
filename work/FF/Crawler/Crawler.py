import logging
import json
import os.path
import sys
import time
import traceback
import urllib
import urllib2

from Config import FF_GET_A_JOB_URL
from Config import FF_REPORT_JOB_URL
from Config import FF_SEND_JSON_REPORT_URL

DEBUG = False

S_COUNT = 0
F_COUNT = 0


class Crawler:

    def generate_json_report(self, comm):

        f = open("crawling_result_real.txt", 'w')

        report = {}
        report['job_info'] = comm.job_info
        report['cerrs'] = []
        report['acc_infos'] = []
        report['last_crawl'] = comm.last_crawl
        report['last_e_msg'] = comm.last_e_msg

        for cerr in comm.cerrs:
            ##make cerr into a dict
            cerr_dict = {}
            cerr_dict['e_msg'] = cerr.e_msg
            cerr_dict['tb_msg'] = cerr.tb_msg

            report['cerrs'].append(cerr_dict)

        for acc_info in comm.acc_infos:
            report['acc_infos'].append(acc_info)

        print "---------------------"

        print report
        f.write(json.dumps(report))
        f.close()

        fp = open("/Temp/json_report.txt","w")
        fp.write(json.dumps(report))
        fp.close()

        return json.dumps(report)

    def send_json_report(self, json_report, comm):
        print json_report
        data = urllib.urlencode({'json_report': json_report})
        if DEBUG:
            req = urllib2.Request(url=FF_SEND_JSON_REPORT_URL, data=data)
        else:
            req = urllib2.Request(url=FF_SEND_JSON_REPORT_URL,data=data)
        upload_result = json.loads(urllib2.urlopen(req).read())
        print "upload_result:"
        print upload_result

        comm.logger.error("upload_result>>> ",upload_result)

        #return {'status': "OK", }
        return upload_result

    def report_job(self, bankdata, e_msg, tb_msg):
        try:
            try:
                job_info_json = json.dumps(self.job_info)
                bankdata_json = json.dumps(bankdata)
                ## TODO : do something about screenshot
            except:
                e_msg = "ERROR_DO_NOT_RETRY_dump_json_for_report_failed"
                tb_msg = traceback.format_exc()
                e_obj = sys.exc_info()
                print e_msg
                print tb_msg
                return (e_msg,tb_msg,e_obj)


            data = urllib.urlencode({'job_info' : job_info_json,
                                         'bankdata' : bankdata_json,
                                         'e_msg' : e_msg,
                                         'tb_msg' : tb_msg,
                                     })
            #print "acc_type: ", self.job_info['acc_type']
            if DEBUG:
                req = urllib2.Request(url="http://54.69.14.22:8081/report-job",data=data)
            else:
                req = urllib2.Request(url=FF_REPORT_JOB_URL,data=data)
            upload_result = json.loads(urllib2.urlopen(req).read())
            print upload_result
            if upload_result['status'].startswith("OK"):
                return ("OK",None,None)
            else:
                raise

        except:
            e_msg = "ERROR_RETRIEABLE_report_job"
            tb_msg = traceback.format_exc()
            e_obj = sys.exc_info()
            print e_msg
            print tb_msg
            return (e_msg,tb_msg,e_obj)

    def get_a_job(self):
        try:
            req = urllib2.Request(url=FF_GET_A_JOB_URL)
            job_info_json = json.loads(urllib2.urlopen(req).read())
            job_info = job_info_json['data'][0]
            print job_info
        except:
            print traceback.format_exc()
            return "ERROR_server down or illegal data received"

        if job_info_json['e_msg']['status'] == 200:
            fp = open("my_job_info.json","w")
            # fp.write(job_info)
            json.dump(job_info, fp)
            fp.close()
            return job_info_json['e_msg']['status']
        elif job_info_json['e_msg']['status'] == 404:
            return job_info_json['e_msg']['status']
        else:
            ##TODO: report to DB?
            print job_info_json['e_msg']['status']
            # raise

    def __init__(self):

        sys.path.append(".")
        sys.path.append("../BankAuth")

        #TODO:check whether i am on azure or ec2 first
        self.platform = 'aws'

        #TODO:check my os
        self.os = 'Windows Server 2012 R2'

        self.job_info = None

        ##this should not fail?
        '''
        if DEBUG:
            self.instance_id = "i-d38ccb16"
        else:
            self.instance_id = urllib2.urlopen("http://instance-data/latest/meta-data/instance-id").read()
        '''

    def run(self):

        global F_COUNT, S_COUNT

        job_status = self.get_a_job()
        if job_status != 200:
            return job_status ##error or wait, i cannot continue

        if not os.path.isfile("my_job_info.json"):
            self.job_info = None
            return "ERROR_i_have_a_job_but_job_file_not_found"

        fp = open("my_job_info.json", "r")
        self.job_info = json.loads(fp.read())
        fp.close()

        #print "run: job_info_status:", self.job_info['status'], self.job_info['job_id']

        ##TODO: choose bank module
        print "mod_name", self.job_info.get('mod_name')
        if self.job_info.get('mod_name') == "WooriSpeed":
            import WooriSpeed as Bank
        elif self.job_info.get('mod_name') == "WooriCard":
            import WooriCard as Bank
        elif self.job_info.get('mod_name') == "WooriBank":
            import WooriBank as Bank
        elif self.job_info.get("mod_name") == "KookminBank":
            import KookminBank as Bank
        elif self.job_info.get("mod_name") == "ShinhanBank":
            import ShinhanBank as Bank
        elif self.job_info.get("mod_name") == "BCCard":
            import BCCard2 as Bank

        else:
            import BCCard2 as Bank
            print "unknown mod_name"
            ##FIXME: This should not happen
            #sys.exit()

        #raise

        comm = Bank.get(job_info=self.job_info, isEncoded=False)

        print "last_e_msg", comm.last_e_msg
        #print comm.__dict__

        try:
            json_report = self.generate_json_report(comm)
        except:
            ##rebuild error to represent json_report_error
            last_e_msg = "ERROR_while_generate_json_report"
            json_report = json.dumps({'last_e_msg' : last_e_msg, })

        try:
            result = self.send_json_report(json_report, comm)

        except:
            print traceback.format_exc()
            #print "send_json_report_result", result
            return "ERROR_while_sending_json_report"

        return result['status']

        #print json_report

if __name__ == "__main__":

    logger = logging.getLogger(__name__)
    #logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add the handlers to the #logger
    fh = logging.FileHandler("crawler_profile.log")
    fh.setLevel(logging.ERROR)
    fh.formatter=formatter
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    ch.formatter=formatter
    logger.addHandler(fh)
    logger.addHandler(ch)

    #time.sleep(5)
    if DEBUG:
        c = Crawler()
        fp = open("my_job_info.json", "r")
        c.job_info = json.loads(fp.read())
        print c.job_info
        fp.close()
        '''
        fp = open("bankdata_test.json", "r")
        bankdata = json.loads(fp.read())
        fp.close()

        c.report_job(bankdata)
        '''
        sys.exit()

    while True:
        c = Crawler()
        status = c.run()
        del c
        if status.startswith("ERROR"):
            print status
            # raise
        elif status.startswith("WAIT"):
            print status
            print "waiting.."

        logger.error("success : " + str(S_COUNT) + " fail : " + str(F_COUNT))

        logger.error("----------------------------------------------")

        time.sleep(60)
