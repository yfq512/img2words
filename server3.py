import cv2
import os, fcntl, time
import model
from apphelper.image import union_rbox,adjust_box_to_origin
from application import trainTicket,idcard
from flask import Flask,render_template,request
import base64
import random

def idcard_ocr(imgpath):
    time.sleep(0.5)
    img = cv2.imread(imgpath)
    _,result,angle= model.model(img,detectAngle=True,config=dict(MAX_HORIZONTAL_GAP=50,MIN_V_OVERLAPS=0.6,MIN_SIZE_SIM=0.6,TEXT_PROPOSALS_MIN_SCORE=0.1,TEXT_PROPOSALS_NMS_THRESH=0.3,TEXT_LINE_NMS_THRESH = 0.7),leftAdjust=True,rightAdjust=True,alph=0.01)

    res = idcard.idcard(result)
    res = res.res
    res =[ {'text':res[key],'name':key,'box':{}} for key in res]

    out_str = {'姓名':None, '性别':None, '民族':None, '出生年月':None, '身份证号码':None, '身份证地址':None}
    for n in res:                                                                                                                                                                           1,1           Top
        key_ = n['name']
        value_ = n['text']
        out_str[key_] = value_
        print(out_str)
    return {'text':out_str}

def getRandomSet(bits):
    num_set = [chr(i) for i in range(48,58)]
    char_set = [chr(i) for i in range(97,123)]
    total_set = num_set + char_set
    value_set = "".join(random.sample(total_set, bits))
    return value_set

app = Flask(__name__)
imgroot = 'test'

@app.route("/idcardocr", methods = ['GET', 'POST'])
def tyocr():
    if request.method == "POST":
        imgbase64 = request.form.get('imgbase64')
        imgdata = base64.b64decode(imgbase64)
        randname = getRandomSet(15)
        imgrandpath = os.path.join(imgroot, randname + '.jpg')
        file = open(imgrandpath,'wb')
        file.write(imgdata)
        file.close()
        res = idcard_ocr(imgrandpath)
        if os.path.exists(imgrandpath):
            os.remove(imgrandpath)
        return res
    else:
        return 'pleas use post'
if __name__ == "__main__":
    print('================= s t a r t ==================')
    host = '0.0.0.0'
    port = '8880'
    app.run(debug=True, host=host, port=port)
