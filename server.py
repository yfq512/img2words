import cv2
import os, fcntl, time
import model
from apphelper.image import union_rbox,adjust_box_to_origin
import requests
from flask import Flask,render_template,request
import base64
import random

#imgroot = 'test'
#locktxt = 'lock.txt'

def find_word(imgpath):
    time.sleep(0.5)
    img = cv2.imread(imgpath)
    _,result,angle= model.model(img,detectAngle=True,config=dict(MAX_HORIZONTAL_GAP=50,MIN_V_OVERLAPS=0.6,MIN_SIZE_SIM=0.6,TEXT_PROPOSALS_MIN_SCORE=0.1,TEXT_PROPOSALS_NMS_THRESH=0.3,TEXT_LINE_NMS_THRESH = 0.7),leftAdjust=True,rightAdjust=True,alph=0.01)
    result = union_rbox(result,0.2)
    res = [{'text':x['text'],'name':str(i),'box':{'cx':x['cx'],'cy':x['cy'],'w':x['w'],'h':x['h'],'angle':x['degree']}} for i,x in enumerate(result)]
    res = adjust_box_to_origin(img,angle, res)##修正box
    txtpath = os.path.join('result', imgpath.split('/')[1].split('.')[0] + '.txt')

    print(res)
    with open(txtpath, 'w') as f:
        for n in res:
            str_temp = n['text']
            f.write(str_temp)
            f.write('\n')
        f.close()
    if os.path.exists(imgpath):
        os.remove(imgpath)

def get_worklist():
    list_ = os.listdir(imgroot)
    if len(list_) == 0:
        if os.path.exists(locktxt):
            try:
                os.remove(locktxt)
            except:
                pass
        return None
    with open(locktxt, 'a') as f:
        try:
            fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
            try:
                list_unwork = os.listdir(imgroot)
                list_working = []
                if os.path.exists(locktxt):
                    for n in open(locktxt):
                        list_working.append(n[:-1])
                for m in list_unwork:
                    if not m in list_working:
                        f.write(m)
                        f.write('\n')
                        fcntl.flock(f, fcntl.LOCK_UN)
                        f.close()
                        return os.path.join(imgroot, m)
                    else:
                        continue
                return None
            except:
                fcntl.flock(f, fcntl.LOCK_UN) ## 一旦程序出现问题，就解锁不要耽误其他进程
                return None
        except:
            return None


def getRandomSet(bits):
    num_set = [chr(i) for i in range(48,58)]
    char_set = [chr(i) for i in range(97,123)]
    total_set = num_set + char_set
    value_set = "".join(random.sample(total_set, bits))
    return value_set

app = Flask(__name__)
imgroot = 'test'
txtroot = 'result'
locktxt = 'lock.txt'

@app.route("/tyocr", methods = ['GET', 'POST'])
def tyocr():
    if request.method == "POST":
        imgbase64 = request.form.get('imgbase64')
        imgdata = base64.b64decode(imgbase64)
        randname = getRandomSet(15)
        imgrandpath = os.path.join(imgroot, randname + '.jpg')
        txtrandpath = os.path.join(txtroot, randname + '.txt')
        file = open(imgrandpath,'wb')
        file.write(imgdata)
        file.close()
        find_word(imgrandpath)
        if os.path.exists(txtrandpath):
            time.sleep(0.1)
            str1 = ''
            for n in open(txtrandpath):
                str1 = str1 + n
        if os.path.exists(imgrandpath):
            os.remove(imgrandpath)
        if os.path.exists(txtrandpath):
            os.remove(txtrandpath)
        return {'text':str1}
    else:
        return 'pleas use post'
if __name__ == "__main__":
    print('================= s t a r t ==================')
    host = '0.0.0.0'
    port = '8090'
    app.run(debug=True, host=host, port=port)

