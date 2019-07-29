import requests
import json
import cv2
import base64
import numpy as np
import ast
import uuid
import time
import re 
ApiKey='HN3C8XlxWURVVe7NGD7TUbU4'
SecretKey='y9xBZWZQXTPYfvjqcDYF6v4GGUsl5vuX'

#获取百度云人脸识别API TOKEN
def get_secret_key():
    url='https://aip.baidubce.com/oauth/2.0/token'
    data={"grant_type":"client_credentials","client_id":ApiKey,"client_secret":SecretKey}
    response=requests.post(url,data=data)
    #print(response.text)
    access_token=json.loads(response.text)['access_token']
    return access_token


def face_detect(img):
    face_recog_url='https://aip.baidubce.com/rest/2.0/face/v3/detect?access_token='+get_secret_key()
    headers={"Content-Type":"application/json"}
    data={
                "image_type":"BASE64",
                "image":img,
                "max_face_num":5,
               "face_field":"gender,beauty,age"   
              }
    data=json.dumps(data)
    response=requests.post(face_recog_url,data=data,headers=headers)
    content = json.loads(response.text)
    return content

def face_recog(img):
    face_recog_url='https://aip.baidubce.com/rest/2.0/face/v3/search?access_token='+get_secret_key()
    headers={"Content-Type":"application/json"}
    data={
                "image_type":"BASE64",
                "image":img,
               "group_id_list":"003",   
              }
    data=json.dumps(data)
    response=requests.post(face_recog_url,data=data,headers=headers)
    content = json.loads(response.text)
    return content

def register(image,user_info):
    face_register_url='https://aip.baidubce.com/rest/2.0/face/v3/faceset/user/add?access_token='+get_secret_key()
    headers={"Content-Type":"application/json"}
    uid=uuid.uuid3(uuid.NAMESPACE_DNS,user_info)
    #print(uid)
    data={
                "image_type":"BASE64",
                "user_id":str(uid).replace('-','_')[1:6],
                "group_id":'003',
                "image":image,
               "user_info":user_info,   
              }
    data=json.dumps(data)
    response=requests.post(face_register_url,data=data,headers=headers)
    content = json.loads(response.text)
    return content
    

if __name__=="__main__":
    video_file_path='./video.mp4'
    cap = cv2.VideoCapture(video_file_path)
    # fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # out = cv2.VideoWriter('output.avi',fourcc, 20.0, (844,1504))
    while(1):
            # 获得图片
            ret, frame = cap.read()
            img_str = cv2.imencode('.jpg', frame)[1].tostring()  # 将图片编码成流数据，放到内存缓存中，然后转化成string格式
            img = base64.b64encode(img_str) # 编码成base64
            #print(type(img))
            #print(frame.shape)
            img=str(img,'utf-8')
            content=face_detect(img)
            print(content)
            # 展示图片
            face_list=content['result']['face_list']
            face_num=content['result']['face_num']
            
            for i in range(face_num):
                face_probability=face_list[i]['face_probability']
                if face_probability<0.6:
                    continue
                else:
                    left_top_x = int(face_list[i]['location']['left'])
                    left_top_y=  int(face_list[i]['location']['top'])
                    right_bottom_x = int(left_top_x + face_list[i]['location']['width'])
                    right_bottom_y =int(left_top_y+ face_list[i]['location']['height'])
                    cv2.rectangle(frame, (left_top_x,left_top_y), (right_bottom_x,right_bottom_y), (0, 0, 255), 2)
                    cutImg = frame[left_top_y:right_bottom_y,left_top_x:right_bottom_x]             #[y1:y2,x1:x2]
                    cut_img_str = cv2.imencode('.jpg', cutImg)[1].tostring()  # 将图片编码成流数据，放到内存缓存中，然后转化成string格式
                    cut_img = str(base64.b64encode(cut_img_str),'utf-8') # 编码成base64
                    gender=face_list[i]['gender']['type']
                    beauty=face_list[i]['beauty']
                    age=face_list[i]['age']
                    user_info="%s,%s,%s"%(gender,age,beauty)
                    register_result=register(cut_img,user_info)
                    print(register_result)
                    recog_result=face_recog(cut_img)
                    print(recog_result,type(recog_result))
                    error_msg=recog_result['error_msg']
                    if error_msg=='SUCCESS':
                        user_info=recog_result['result']['user_list'][0]['user_info']                   
                        #print(user_info,type(user_info))
                        # print(user_age,user_beauty,user_gender)
                        #cv2.imwrite("cut1.jpg", cutImg)
                        #标注文本
                        #text = '性别:%s,年龄:%s,颜值:%s'%(user_gender,user_age,user_beauty)
                        info=user_info.split(',')
                        age=info[1]
                        #print(age)
                        text='age:%s'%age
                        #print(type(frame))
                        cv2.putText(frame, text, (left_top_x, left_top_y),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 1) 
                    else:
                        print('照片中无人脸!')
                        continue

            cv2.imshow("capture", frame)
            #out.write(frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):            
                break
