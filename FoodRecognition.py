import requests
import io
from PIL import Image
import numpy as np
import cv2
import os
import json
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


class FoodRecognition:
    image_path = ""
    res_tuple = (None, 0)
    camera_image_save_path = "E:\\dataset\\food_recognition\\image_operation_file"
    url_local = "https://southcentralus.api.cognitive.microsoft.com/customvision/v3.0/Prediction/3cb043" \
                "b6-e2ae-4c6d-974f-82bfd5bc780c/classify/iterations/Food-detection(food%20domain)/image"
    content_type = "application/octet-stream"
    prediction_key = "9677b0bca73445f3835579b7e94c4f70"

    def get_probability(self):
        return self.res_tuple[1]

    def get_result(self):
        return self.res_tuple[0]

    def get_image_path(self):
        return self.image_path

    def set_path(self, s):
        self.path = s

    def convert_pil_image_to_byte_array(self, img):
        img_byte_array = io.BytesIO()
        img.save(img_byte_array, format='JPEG', subsampling=0, quality=100)
        img_byte_array = img_byte_array.getvalue()
        return img_byte_array

    def test_local(self, img):

        img_bin = self.convert_pil_image_to_byte_array(img)
        headers = {
            "Prediction-Key": self.prediction_key,
            "Content-Type": self.content_type
        }
        res = requests.post(url=self.url_local, headers=headers, data=img_bin)
        result_string = res.content.decode("unicode_escape")
        # print("result: " + result)

        return result_string

    def print_str(self, s):
        dic = eval(s)
        # res = json.dumps(dic)
        res = json.dumps(dic, indent=4)
        print(res)
        return res

    def convert_str2dic(self, s):
        i = s.find("predictions")
        l = len(s)
        res = {}  # dict
        k = 0
        while k < 10:
            if s.find("probability", i):
                i = s.find("probability", i)
                i = i + 13
                # print(s[i:i+20])
                # print("find_number")
                num = self.find_number(s[i:i+20])
                # print(num)
                # print(i)
                pro = float(num)
                # print(pro)
                i = s.find("tagName", i)
                i = i + 10
                tag = self.find_digit(s[i:l])
                # print(tag)
                res[tag] = pro
            else:
                break
            k = k + 1

        return res  # dict

    def find_number(self, s):
        l = len(s)
        res = ""
        i = 0
        while i < l:
            if '0' <= s[i] <= '9' or s[i] == '.' or s[i] == 'e' or s[i] == '-' or s[i] == 'E':
                res = res + s[i]
            else:
                break
            i = i + 1
        return res  # string

    def find_digit(self, s):
        l = len(s)
        res = ""
        i = 0
        while i < l:
            if 'a' <= s[i] <= 'z' or s[i] == '_':
                res = res + s[i]
            else:
                break
            i = i + 1
        return res  # sting

    def find_most_likely_food(self, dic):
        res_probability = 0
        res_food_type = ""
        for key in dic:
            if dic[key] > 0.5 and dic[key] > res_probability:
                res_probability = dic[key]
                res_food_type = key
        res_tuple = (res_food_type, res_probability)
        return res_tuple  # tuple

    def count_camera_number(self):
        cnt = 0
        for i in range(0, 10):
            if cv2.VideoCapture(i, cv2.CAP_DSHOW).grab() is True:
                cnt = cnt + 1
                # print(i)
        return cnt

    def camera(self, camera_index):
        index = 1
        cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        width = 640
        height = 480
        w = 360
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        crop_w_start = (width - w) // 2
        crop_h_start = (height - w) // 2
        while True:
            # get a frame
            ret, frame = cap.read()
            # show a frame
            frame = frame[crop_h_start:crop_h_start + w, crop_w_start:crop_w_start + w]
            frame = cv2.flip(frame, 1, dst=None)
            cv2.imshow("capture", frame)

            input = cv2.waitKey(1) & 0xFF

            if input == ord('x'):
                output_path = "%s/%d.jpeg" % (self.camera_image_save_path, index)
                cv2.imwrite(output_path,
                            cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA))
                # print("%s: %d 张图片" % (class_name, index))
                break

            if input == 27:  # esc
                output_path = None
                break

        cap.release()
        cv2.destroyAllWindows()
        return output_path

    def local_image_recognition(self, path):
        if path is None or len(path) == 0:
            return
        self.image_path = path
        raw_image = Image.open(self.image_path)
        result_string = self.test_local(raw_image)
        res_dic = self.convert_str2dic(result_string)
        self.res_tuple = self.find_most_likely_food(res_dic)

    def camera_image_recognition(self, camera_index):
        self.image_path = self.camera(camera_index)
        if self.image_path is None or len(self.image_path) == 0:
            return None
        raw_image = Image.open(self.image_path)
        result_string = self.test_local(raw_image)
        res_dic = self.convert_str2dic(result_string)
        self.res_tuple = self.find_most_likely_food(res_dic)
    # Press the green button in the gutter to run the script.

# See PyCharm help at https://www.jetbrains.com/help/pycharm/