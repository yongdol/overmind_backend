# -*- coding: utf-8 -*-

import logging
import traceback
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException,NoAlertPresentException
import StringIO
from PIL import Image
import base64

SC = ""
SC_IMG = 'err_'
IMG_EXT = '.jpg'


class CErr:
    def __init__(self, e_msg, tb_msg=None, sc=None):

        if not isinstance(e_msg, basestring):
            raise

        self.e_msg = e_msg
        self.tb_msg = tb_msg
        self.sc = sc


#comm = Comm(job_info)
#comm = Comm(job_info,isEncoded=False)
#comm = Comm(job_info,error_level=ERROR,driver=driver)

class Comm:
    def __init__(self, job_info, **kwargs):

        self.sc_num = 0

        self.job_info = job_info
        self.driver = None
        self.page_source = None
        self.url = None

        self.cred_decoded = None

        self.log_level = "ERROR"
        #notset debuginfo warning error critical

        self.isEncoded = True

        self.acc_infos = []
        self.acc_info = None

        self.last_crawl = None

        self.last_e_msg = "ERROR_last_e_msg_initiated"
        #self.tb_msg = None

        self.logger = logging.getLogger(__name__)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.fh = logging.FileHandler("file.log")
        self.ch = logging.StreamHandler()
        self.log_file_name = None

        if self.log_level == "CRITICAL":
            self.ch.setLevel(logging.CRITICAL)
            self.fh.setLevel(logging.CRITICAL)
        elif self.log_level == "ERROR":
            self.ch.setLevel(logging.ERROR)
            self.fh.setLevel(logging.ERROR)

        self.fh.formatter = self.formatter
        self.ch.formatter = self.formatter

        self.logger.addHandler(self.fh)
        self.logger.addHandler(self.ch)

        self.cerrs = []

        self.DEBUG_COUNTER_01 = 0

        self.set_attr(**kwargs)

    def set_attr(self, **kwargs):

        if 'job_info' in kwargs:
            self.job_info = kwargs['job_info']
        if 'isEncoded' in kwargs:
            self.isEncoded = kwargs['isEncoded']
        if 'driver' in kwargs:
            self.driver = kwargs['driver']
        if 'last_e_msg' in kwargs:
            self.last_e_msg = kwargs['last_e_msg']
        if 'cred_decoded' in kwargs:
            self.cred_decoded = kwargs['cred_decoded']
        #if kwargs.has_key('acc_info'):
        #    self.acc_info = kwargs['acc_info']
        if 'logger' in kwargs:
            self.logger = kwargs['logger']
        if 'url' in kwargs:
            self.url = kwargs['url']
        if 'cred_encoded' in kwargs:
            self.url = kwargs['cred_encoded']
        if 'acc_infos' in kwargs:
            self.acc_infos = kwargs['acc_infos']
        if 'page_source' in kwargs:
            self.page_source = kwargs['page_source']
        if 'log_file_name' in kwargs:
            self.log_file_name = kwargs['log_file_name']
            self.logger.removeHandler(self.fh)
            self.fh = logging.FileHandler(self.log_file_name)

            if self.log_level == "CRITICAL":
                self.fh.setLevel(logging.CRITICAL)
            elif self.log_level == "ERROR":
                self.fh.setLevel(logging.ERROR)

            self.fh.formatter = self.formatter

            self.logger.addHandler(self.fh)

    def add_err(self, e_msg, **kwargs):

        self.sc_num += 1
        sc_name = SC_IMG + str(self.sc_num) + IMG_EXT

        tb_msg = None
        if 'tb_msg' in kwargs:
            tb_msg = kwargs['tb_msg']
            self.logger.error(">>> " + kwargs['tb_msg'])

        self.logger.error(">>> " + e_msg)

        sc=None
        if 'SC' in kwargs:
            sc = kwargs['SC']

        sc_data = None
        if sc:
            sc_data = self.get_screenshot_data(sc_name)

        cerr = CErr(e_msg, tb_msg, sc_data)
        self.last_e_msg = e_msg

        self.cerrs.append(cerr)

    def get_screenshot_data(self, sc_name):

        try:
            if self.driver is None:
                self.logger.error("ERROR_THERE_IS_NO_WEBDRIVER")
                return None
            else:
                self.driver.save_screenshot(sc_name)
                im = Image.open(sc_name)
                output = StringIO.StringIO()
                im.save(output, 'PNG')
                contents = output.getvalue()
                output.close()
                return contents
        except:
            self.logger.error("error in save log screenshot")
            self.logger.error("tb msg>>" + traceback.format_exc())
            return None