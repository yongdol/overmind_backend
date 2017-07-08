import urllib2,urllib
import mechanize
import random,traceback
import time,sys,datetime

url = "http://54.69.14.22:8081/register-banking-demo-form"

acc_no_list = ['01866145102001','1002442773027','1002853743257','27008391402001']
acc_no_list2 = ['1002429877703','1002147008626']
br = mechanize.Browser()

flag = 1

while(True):
    r = random.randrange(0,4)
    r2 = random.randrange(0,2)
    br.open(url)

    for form in br.forms():
        if form.attrs['id'] == 'login-form':
            br.form = form
            br.form['dsource_id']=['3',]

            if flag == 1:
                br.form['cred_user_id']='zakk95'
                br.form['cred_user_pw']='uE^9z@'
                br.form['cred_acc_no']=str(acc_no_list[r])
                flag = 2
            elif flag == 2:
                br.form['cred_user_id']='hawaii25'
                br.form['cred_user_pw']='!@#Lee314'
                br.form['cred_acc_no']='1005202939785'
                flag = 3
            elif flag == 3:

                br.form['cred_user_id']='hxk1300'
                br.form['cred_user_pw']='joon#12'
                br.form['cred_acc_no']=str(acc_no_list2[r2])
                flag = 1


    br.submit()

    now = time.localtime()

    s = "%04d-%02d-%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)

    print "job is fetched at >> ",s

    time.sleep(55)






