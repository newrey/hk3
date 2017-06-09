#-*- coding: UTF-8 -*- 
from flask import Flask, request
from bs4 import BeautifulSoup
import requests,json,pickle,os
from flask_restful import Resource, Api
# from urllib import unquote
# reload(sys)
# sys.setdefaultencoding('utf-8')

HOST='http://103.82.55.91'
LOGIN_PAGE='/Default.aspx'
app = Flask(__name__)
api = Api(app)


class EAM_ROOT(Resource):
    def get(self):
        return {'hello': request.args.get('abc')}

class EAM_LOGIN(Resource):
    def post(self):
        username = request.form['username'] #'eam2'
        password = request.form['password'] #'1'
        loginRequest = requests.get(HOST+LOGIN_PAGE)
        __VIEWSTATE = BeautifulSoup(loginRequest.content,"html.parser").find(id='__VIEWSTATE')
        cookies = loginRequest.cookies
        sessionId = cookies['ASP.NET_SessionId']
        checkCodeRequest = requests.get(HOST+'/ValidateCode.aspx',cookies=cookies)
        cookies = checkCodeRequest.cookies
        CheckCode = cookies['CheckCode']
        cookies = checkCodeRequest.cookies
        loginVerifyRequest = requests.post(HOST+LOGIN_PAGE,cookies=cookies,data={
            'UserName': username, 
            'UserPass': password,
            'checktext':CheckCode,
            '__VIEWSTATE':__VIEWSTATE['value'],
            '__LASTFOCUS':'',
            '__EVENTTARGET':'',
            '__EVENTARGUMENT':'',
            'LoginBtn.x':'0',
            'LoginBtn.y':'0'
        })
        if len(BeautifulSoup(loginVerifyRequest.content,"html.parser").find_all('frame',src='initmain.aspx')) == 1:
            return {'logined':True,'status':True , 'sid':loginVerifyRequest.cookies['ASP.NET_SessionId'],'haoke':loginVerifyRequest.cookies['haoke']}
        else:
            return {'logined':False,'status':False , 'message':'登陆失败，请检查用户名和密码'}

class EAM_DETAIL(Resource):
    def get(self):
        wpbm = request.args.get("wpbm") #'2017050505'#
        cfdd = request.args.get("cfdd")
        sessionId = request.args.get("sid") # #
        haoke = 'deptname=%b9%ab%cb%be%b1%be%b2%bf&pagecount=20&sdate=2017-05-01' #request.args.get("haoke")
        if(sessionId == '' or haoke == ''):
            return {'status':False,"message":"sid haoke null"}
        cookies = {'ASP.NET_SessionId' : sessionId,'haoke' : haoke}
        __VIEWSTATE = self.getDetail(cookies = cookies)
        if __VIEWSTATE == '':
            return {'logined':False,'status':True,'message': '需要登陆'}
        zcwhRequest = requests.post(HOST + '/eam2/zcgl/Zcwh.aspx',cookies = cookies,data={
            '__VIEWSTATE':__VIEWSTATE,
            'wpbm':wpbm,
            'cfdd':cfdd,
            'wpmc':'',
            'wptxm':'',
            'gzfs':'',
            'sybm':'',
            'cqdw':'',
            'wpzt':'',
            'bgrmc':'',
            'syrmc':'',
            'ssfl':'',
            'QueryBtn':'%B2%E9%D1%AF'
        })
        hkHeadStyle = BeautifulSoup(zcwhRequest.content,"html.parser").find(attrs={"class": "hkHeadStyle"})
        if hkHeadStyle is None:
            return {'logined':True,'status':False,'message':'没有找到对应资产',"results":[]}
        tr = hkHeadStyle.find_all_next("tr")
        results = []
        for x in tr:
            tr_result = []
            for td in x.find_all("td"):
                tdtext = td.get_text().replace("\n","")
                tr_result.append(tdtext)
            results.append(tr_result)
        results.pop()
        return {'logined':True,'status':True,'message':__VIEWSTATE,"results":results}

    def getDetail(self,cookies):
        zcwh = requests.get(HOST + '/eam2/zcgl/zcwh.aspx',cookies=cookies)
        __VIEWSTATE = BeautifulSoup(zcwh.content,"html.parser").find(id='__VIEWSTATE')
        if __VIEWSTATE is None:
            return ''
        else:
            return __VIEWSTATE['value']

class EAM_CFDD(Resource):
    def get(self):
        sessionId = request.args.get("sid") #'1omi4gnzi4u0mq1ghdjh4r5i'
        haoke = 'deptname=%b9%ab%cb%be%b1%be%b2%bf&pagecount=20&sdate=2017-05-01' #request.args.get("haoke")
        if(sessionId == '' or haoke == '' or sessionId is None):
            return {'status':False,"message":"sid haoke null"}
        cookies = {'ASP.NET_SessionId' : sessionId,'haoke' : haoke}
        zcwh = requests.get(HOST + '/eam2/zcgl/zcwh.aspx',cookies=cookies)
        __VIEWSTATE = BeautifulSoup(zcwh.content,"html.parser").find(id='__VIEWSTATE')
        if __VIEWSTATE is None:
            return {'logined':False ,'status':True,'message':'需要登陆'}
        cfdd = BeautifulSoup(zcwh.content,"html.parser").find(id='cfdd')
        results = [{"value":x['value'],"text":x.get_text()} for x in cfdd.find_all("option")]
        results.pop(0)
        return {'logined':True ,'status':True,'message':__VIEWSTATE['value'],"results":results}

class EAM_BIND(Resource):
    dataFile = 'data.pkl'
    def post(self):
        oneCode = request.args.get("oneCode")
        rfidCode = request.args.get("rfidCode")
        if os.path.exists(self.dataFile):
            pkl_file = open(self.dataFile, 'rb')
            data = dict(pickle.load(pkl_file))
            pkl_file.close()
        else:
            data = dict()
        if rfidCode in data:
            return {'logined':True ,'status':False,'message': oneCode+'已经绑定'+ data.get(rfidCode)}
        else:
            output = open(self.dataFile, 'wb')
            data[rfidCode]=oneCode
            pickle.dump(data, output)
            output.close()
            return {'logined':True, 'status':True,'message': '绑定成功'}

    def get(self):
        rfidCode = request.args.get("rfidCode")
        if os.path.exists(self.dataFile):
            pkl_file = open(self.dataFile, 'rb')
            data = dict(pickle.load(pkl_file))
            pkl_file.close()
        else:
            data = dict()
        if rfidCode in data:
            return {'logined':True,'status':True,'message':data.get(rfidCode)}
        else:
            return {'logined':True,'status':False,'message':'尚未绑定'}


api.add_resource(EAM_ROOT, '/')
api.add_resource(EAM_LOGIN, '/login')
api.add_resource(EAM_DETAIL, '/detail')
api.add_resource(EAM_CFDD, '/cfdd')
api.add_resource(EAM_BIND, '/bind')

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')