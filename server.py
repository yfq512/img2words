import os, requests, time, cv2
from flask import Flask,render_template,request
import base64
import random

def getRandomSet(bits):
    num_set = [chr(i) for i in range(48,58)]
    char_set = [chr(i) for i in range(97,123)]
    total_set = num_set + char_set
    value_set = "".join(random.sample(total_set, bits))
    return value_set

app = Flask(__name__)
imgroot = 'test'
txtroot = 'result'

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
        img = cv2.imread(imgrandpath)
        try:
            img.shape
            print('img is OK')
        except:
            return {'sign':-1, 'text':'img error'}

        count = 0
        while True:
            time.sleep(0.01)
            count = count + 0.01
            if count > 20:
                return {'sign':-1, 'text':'time out'}
            if os.path.exists(txtrandpath):
                time.sleep(0.1)
                str1 = ''
                for n in open(txtrandpath):
                    str1 = str1 + n[:-1]
                print(str1)
                os.remove(txtrandpath)
                return {'sign':0, 'text':str1}

            else:
                continue
    else:
        return "<h1>Image find words! please use post</h1>"

if __name__ == "__main__":
    host = '0.0.0.0'
    port = '8090'
    app.run(debug=True, host=host, port=port)
