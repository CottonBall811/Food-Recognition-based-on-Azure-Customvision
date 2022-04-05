# -*-coding:utf-8-*-
import PySimpleGUI as sg
from FoodRecognition import FoodRecognition
from PIL import Image
import base64


def image_operate(infile_path, x_size, y_size, outfile_path):
    if infile_path is None or len(infile_path) == 0:
        return None
    in_img = Image.open(infile_path)
    (x, y) = in_img.size
    if x_size / x > y_size / y:
        x_size = int(x * y_size / y)
    else:
        y_size = int(y * x_size / x)
    out_img = in_img.resize((x_size, y_size), Image.ANTIALIAS)
    index = 1
    out_path = "%s/%d.png" % (outfile_path, index)
    out_img.save(out_path)
    return out_path


def convert_image2base64(image_path):
    with open(image_path, 'rb') as f:
        image = f.read()
    image_base64 = str(base64.b64encode(image), encoding='utf-8')
    return image_base64


def use_my_theme():
    my_new_theme1 = {'BACKGROUND': '#005B87',
                    'TEXT': '#E3ECF1',
                    'INPUT': '#E3ECF1',
                    'TEXT_INPUT': '#000000',
                    'SCROLL': '#c7e78b',
                    'BUTTON': ('white', '#004265'),
                    'PROGRESS': ('#01826B', '#D0D0D0'),
                    'BORDER': 1,
                    'SLIDER_DEPTH': 0,
                    'PROGRESS_DEPTH': 0}
    sg.theme_add_new('MyNewTheme1', my_new_theme1)
    sg.theme('MyNewTheme1')


if __name__ == '__main__':
    # set parameters
    image_camera_png_path = "E:\\a1文件\\temp\\微软实习\\camera.png"
    image_local_picture_png_path = "E:\\a1文件\\temp\\微软实习\\local.png"
    image_photo_png_path = "E:\\a1文件\\temp\\微软实习\\photo.png"
    out_file_path = "E:\\dataset\\food_recognition\\image_operation_file"
    image_camera_and_local_x_size = 200
    image_camera_and_local_y_size = 200
    image_photo_x_size = 400
    image_photo_y_size = 200
    text_result_x_length = 25
    text_result_y_length = 1
    text_title_x_length = 20
    text_title_y_length = 1
    text_hint_x_length = 22
    text_hint_y_length = 1
    # set the theme
    use_my_theme()

    # components
    text_title = sg.T('Food recognition', size=(text_title_x_length, text_title_y_length))
    image_camera_adjust_path = image_operate(infile_path=image_camera_png_path, x_size=image_camera_and_local_x_size,
                                             y_size=image_camera_and_local_y_size, outfile_path=out_file_path)
    camera_base64 = convert_image2base64(image_camera_adjust_path)
    button_camera = sg.Button('', image_data=camera_base64,
                              button_color=(sg.theme_background_color(), sg.theme_background_color()),
                              border_width=0, key='Camera')
    image_local_picture_adjust_path = image_operate(infile_path=image_local_picture_png_path,
                                                    x_size=image_camera_and_local_x_size,
                                                    y_size=image_camera_and_local_y_size, outfile_path=out_file_path)
    local_picture_base64 = convert_image2base64(image_path=image_local_picture_adjust_path)
    button_local = sg.Button('', image_data=local_picture_base64,
                             button_color=(sg.theme_background_color(), sg.theme_background_color()),
                             border_width=0, key='Local Picture')
    button_exit = sg.B('Exit')
    text_str_result = sg.T('                                       Result:',
                           size=(text_result_x_length, text_result_y_length))
    text_str_probability = sg.T('                                 Probability:',
                                size=(text_result_x_length, text_result_y_length))
    text_food_type = sg.T(None, key='-OUT1-', size=(text_result_x_length, text_result_y_length))
    text_probability = sg.T(None, key='-OUT2-', size=(text_result_x_length, text_result_y_length))
    image_photo_adjust_path = image_operate(infile_path=image_photo_png_path, x_size=image_photo_x_size,
                                            y_size=image_photo_y_size, outfile_path=out_file_path)
    image_photo = sg.Image(image_photo_adjust_path, key='-IMG-', size=(image_photo_x_size, image_photo_y_size))
    text_hint = sg.T('', key='-HINT-', size=(text_hint_x_length, text_hint_y_length))

    # set the layout
    layout = [[sg.T('                                    '), text_title],  # space is for centered
              [button_local, button_camera],
              [image_photo],
              [text_str_result, text_food_type],
              [text_str_probability, text_probability],
              [text_hint, button_exit]]  # space is for centered

    # set the window
    window = sg.Window('Food recognition', layout)

    fr = FoodRecognition()

    while True:
        event, values = window.read()

        # event recognition
        if event in ("Camera", "Local Picture"):
            if event == "Camera":
                camera_number = fr.count_camera_number()
                camera_index = sg.popup_get_text("You have %d camera, which one do you want (from 0 to %d, default 0)"
                                                 % (camera_number, camera_number-1))
                if camera_index is None:
                    camera_index = 0
                fr.camera_image_recognition(int(camera_index))
                img_path = fr.get_image_path()
            else:
                img_path = sg.popup_get_file("Please choose the file")
                window['-HINT-'].update("Waiting")
                fr.local_image_recognition(path=img_path)
            probability = fr.get_probability()
            food_type = fr.get_result()
            img_adjust = image_operate(infile_path=img_path, x_size=image_photo_x_size, y_size=image_photo_y_size,
                                       outfile_path=out_file_path)
            window['-IMG-'].update(filename=img_adjust)  # show the image that user want to recognize

            if probability > 0.5:  # successful recognition
                window['-HINT-'].update("Success")
                window['-OUT1-'].update(food_type)
                window['-OUT2-'].update(str(probability))
            else:  # failing recognition
                window['-HINT-'].update("Fail")
                window['-OUT1-'].update('I cannot identify it')
                window['-OUT2-'].update(str(probability))

        # event exit
        if event in (None, "Exit"):  # click the exit button
            break

    window.close()
