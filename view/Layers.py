import typing

import PySimpleGUI as sg
from model.TypeShots import AngleShot, LevelShot, ScaleShot, TypeShot

from control.default_values import *

from PIL import Image, ImageDraw
import io
from base64 import b64encode, b64decode


def generate_btn_circle(color: str, size: typing.Tuple[int, int]) -> bytes:
    btn_img = Image.new('RGBA', size, (0, 0, 0, 0))
    d = ImageDraw.Draw(btn_img)
    d.ellipse((0, 0, size[0], size[1]), fill=color)
    data = io.BytesIO()
    btn_img.save(data, format='png', quality=95)
    return b64encode(data.getvalue())


# Layout settings and videoplayer
element_frame_loader_file = sg.Frame('Load video',
                                     [
                                         [sg.Input(visible=True, size=42, enable_events=True, key='_FILEBROWSE_',
                                                   justification='right', readonly=True),
                                          sg.FileBrowse(button_text="Load", file_types=(
                                              ('MP4 File', '*.mp4'), ('MKV File', '*.mkv')))],
                                         [sg.Text("Please select a video file", key='_FILEBROWSE_TEXT_')]
                                     ])

element_frame_selector_features = sg.Frame('Select camera features to extract',
                                           [[sg.Checkbox(type_shot.value, default=default_checkbox_type,
                                                         key='_CHECKBOX_{}_'.format(type_shot.name),
                                                         enable_events=True)] for type_shot in TypeShot])

"""
[
   [sg.Checkbox('Angle Shots', default=default_checkbox_angle,
                key='_CHECKBOX_{}_'.format(TypeShot.ANGLE.name),
                enable_events=True)],
   [sg.Checkbox('Level Shots', default=default_checkbox_level,
                key='_CHECKBOX_{}_'.format(TypeShot.LEVEL.name),
                enable_events=True)],
   [sg.Checkbox('Scale Shots', default=default_checkbox_scale,
                key='_CHECKBOX_{}_'.format(TypeShot.SCALE.name),
                enable_events=True)]
]
"""

# Not used
"""
element_frame_selector_start = sg.Frame('Start video from:',
                                        [[sg.Column([
                                            [sg.Radio("The Beginning", "StartRadio", True,
                                                      key="_RADIO_START_ZERO_",
                                                      enable_events=True)],
                                            [sg.Radio("From Frame", "StartRadio", False, key="_RADIO_START_FRAME_",
                                                      enable_events=True)],
                                            [sg.pin(sg.Column([[sg.Text("0000", key="_INDICATOR_START_FRAME_")], [
                                                sg.Slider(range=(0, 500), default_value=0, size=(20, 15),
                                                          orientation='horizontal',
                                                          disable_number_display=True,
                                                          enable_events=True,
                                                          key="_SLIDER_START_FRAME_")], ],
                                                              visible=True, key="column_frame_select"))],
                                            [sg.Radio("From Time", "StartRadio", False, key="_RADIO_START_TIME_",
                                                      enable_events=True)],
                                            [sg.pin(sg.Column([[sg.Text("00:00", key="_INDICATOR_START_TIME_")], [
                                                sg.Slider(range=(0, 500), default_value=0, size=(20, 15),
                                                          orientation='horizontal',
                                                          disable_number_display=True,
                                                          enable_events=True,
                                                          key="_SLIDER_START_TIME_")], ],
                                                              visible=True, key="column_seconds_select"))],
                                        ])]])
"""

element_frame_selector_frame_extracts = sg.Frame('Frames extraction frequency', [
    [
        sg.Text("Capture 1 frame every "),
        sg.Spin(values=[i for i in range(1, 8)], initial_value=default_delta_frames, size=(3, 1),
                key="_RATIO_FRAMES_CAPTURE_",
                enable_events=True),
        sg.Text(" seconds")
    ]
])

element_load_from_csv = sg.Frame('Load annotations from CSV file',
                                 [
                                     [sg.Input(visible=True, size=42, enable_events=True, key='_BTN_LOAD_CSV_',
                                               justification='right', readonly=True),
                                      sg.FileBrowse(button_text="Load from CSV file", file_types=(
                                          ("CSV File", "*.csv"),))],
                                     [sg.Text("Please select a CSV file", key='_TXT_CSV_LOADED_')]
                                 ])

element_right_selector = sg.Column([
    [element_frame_selector_frame_extracts],
    [element_load_from_csv]
])

layout_settings = [
    [element_frame_loader_file],
    [element_frame_selector_features, element_right_selector],
]

layout_loading_btn = [
    [sg.Button("Load video and settings", key='_BTN_LOAD_VIDEO_', disabled=True),
     sg.Button("Reset", key='_BTN_RESET_VIDEO_', disabled=True)]
]

layout_video_frame = [
    [sg.Image(filename="", key="_IMAGE_VIDEOPLAYER_", size=size_videoplayer_frame,
              background_color='black')],
    [sg.Text("00:00 / 0000", key="_TIME_FRAME_PROGRESS_BAR_"),
     sg.ProgressBar(max_value=100, orientation='h', size=(30, 10), key="_PROGRESS_BAR_VIDEO_"),
     sg.Text("00:00 / 0000", key="_TOTAL_TIME_FRAME_PROGRESS_BAR_")],
]

layout_videoplayer_options = [
    [sg.Column(layout_settings, element_justification='c', key='_COLUMN_SETTINGS_')],
    [sg.HorizontalSeparator()],
    [sg.Column(layout_loading_btn, element_justification='c', key='_COLUMN_LOADING_BTN_')],
    [sg.Column(layout_video_frame, element_justification='c', key='_COLUMN_VIDEO_FRAME_')],
]

# -------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------

btn_red_base64 = generate_btn_circle('red', (25, 25))
btn_green_base64 = generate_btn_circle('green', (25, 25))

layout_angle_view = sg.Frame(TypeShot.ANGLE.value,
                             [[sg.Text(angle_shot_select.value), sg.Button(image_data=btn_red_base64,
                                                                           key='_BTN_SHOT_{}_{}_'.format(
                                                                               TypeShot.ANGLE.name,
                                                                               angle_shot_select.name),
                                                                           disabled=True)] for angle_shot_select in
                              AngleShot],
                             element_justification='r', title_location=sg.TITLE_LOCATION_TOP,
                             key='_FRAME_{}_BUTTONS_'.format(TypeShot.ANGLE.name))

layout_frames_extract_shot_view = [
    [sg.Column([[sg.Button("<<", key='_BACKWARD_DELTA_FRAME_BUTTON_', disabled=True),
                 sg.Button("<", key='_BACKWARD_ONE_FRAME_BUTTON_', disabled=True),
                 sg.Button("Play", key='_PLAY_PAUSE_BUTTON_', disabled=True),
                 sg.Button("Call model prediction", key="_BTN_MANUAL_EXTRACTION_", disabled=True),
                 sg.Button(">", key='_FORWARD_ONE_FRAME_BUTTON_', disabled=True),
                 sg.Button(">>", key='_FORWARD_DELTA_FRAME_BUTTON_', disabled=True)]], key='_CONTROL_GROUP_BTN_')],
    [sg.Image(filename="", key="_IMAGE_ANNOTATION_", size=size_annotation_frame, background_color='black')],
    [sg.Frame(TypeShot.SCALE.value,
              [[sg.Column([[sg.Text(scale_shot_select.value)], [sg.Button(image_data=btn_red_base64,
                                                                          key='_BTN_SHOT_{}_{}_'.format(
                                                                              TypeShot.SCALE.name,
                                                                              scale_shot_select.name),
                                                                          disabled=True)]],
                          element_justification='c') for scale_shot_select in ScaleShot]],
              element_justification='l', title_location=sg.TITLE_LOCATION_TOP,
              key='_FRAME_{}_BUTTONS_'.format(TypeShot.SCALE.name))],
]

layout_level_view = sg.Frame(TypeShot.LEVEL.value, [[sg.Button(image_data=btn_red_base64,
                                                               key='_BTN_SHOT_{}_{}_'.format(TypeShot.LEVEL.name,
                                                                                             level_shot_select.name),
                                                               disabled=True),
                                                     sg.Text(level_shot_select.value)] for level_shot_select in
                                                    LevelShot],
                             element_justification='l', title_location=sg.TITLE_LOCATION_TOP,
                             key='_FRAME_{}_BUTTONS_'.format(TypeShot.LEVEL.name))

"""
sg.Frame(TypeShot.ANGLE.value,
                             [
                                 [sg.Text(AngleShot.OVERHEAD.value), sg.Button(image_data=btn_red_base64,
                                                                               key='_BTN_SHOT_{}_{}_'.format(
                                                                                   TypeShot.ANGLE.name,
                                                                                   AngleShot.OVERHEAD.name),
                                                                               disabled=True)],
                                 [sg.Text(AngleShot.HIGH.value), sg.Button(image_data=btn_red_base64,
                                                                           key='_BTN_SHOT_{}_{}_'.format(
                                                                               TypeShot.ANGLE.name,
                                                                               AngleShot.HIGH.name),
                                                                           disabled=True)],
                                 [sg.Text(AngleShot.NOANGLE.value), sg.Button(image_data=btn_red_base64,
                                                                              key='_BTN_SHOT_{}_{}_'.format(
                                                                                  TypeShot.ANGLE.name,
                                                                                  AngleShot.NOANGLE.name),
                                                                              disabled=True)],
                                 [sg.Text(AngleShot.LOW.value), sg.Button(image_data=btn_red_base64,
                                                                          key='_BTN_SHOT_{}_{}_'.format(
                                                                              TypeShot.ANGLE.name,
                                                                              AngleShot.LOW.name),
                                                                          disabled=True)],
                                 [sg.Text(AngleShot.DUTCH.value), sg.Button(image_data=btn_red_base64,
                                                                            key='_BTN_SHOT_{}_{}_'.format(
                                                                                TypeShot.ANGLE.name,
                                                                                AngleShot.DUTCH.name),
                                                                            disabled=True)]
                             ], element_justification='r', title_location=sg.TITLE_LOCATION_TOP,
                             key='_FRAME_{}_BUTTONS_'.format(TypeShot.ANGLE.name))
"""
"""
    [sg.Frame(TypeShot.SCALE.value,
              [[
                  sg.Column([[sg.Text(ScaleShot.LONG.value)], [sg.Button(image_data=btn_red_base64,
                                                                         key='_BTN_SHOT_{}_{}_'.format(
                                                                             TypeShot.SCALE.name,
                                                                             ScaleShot.LONG.name),
                                                                         disabled=True)]],
                            element_justification='c'),
                  sg.Column([[sg.Text(ScaleShot.MEDIUM.value)], [sg.Button(image_data=btn_red_base64,
                                                                           key='_BTN_SHOT_{}_{}_'.format(
                                                                               TypeShot.SCALE.name,
                                                                               ScaleShot.MEDIUM.name),
                                                                           disabled=True)]],
                            element_justification='c'),
                  sg.Column([[sg.Text(ScaleShot.CLOSE.value)], [sg.Button(image_data=btn_red_base64,
                                                                          key='_BTN_SHOT_{}_{}_'.format(
                                                                              TypeShot.SCALE.name,
                                                                              ScaleShot.CLOSE.name),
                                                                          disabled=True)]],
                            element_justification='c')
              ]], element_justification='c', title_location=sg.TITLE_LOCATION_TOP,
              key='_FRAME_{}_BUTTONS_'.format(TypeShot.SCALE.name))

     ],
"""
"""
layout_level_view = sg.Frame(TypeShot.LEVEL.value,
                             [
                                 [sg.Button(image_data=btn_red_base64,
                                            key='_BTN_SHOT_{}_{}_'.format(TypeShot.LEVEL.name, LevelShot.AERIAL.name),
                                            disabled=True),
                                  sg.Text(LevelShot.AERIAL.value)],
                                 [sg.Button(image_data=btn_red_base64,
                                            key='_BTN_SHOT_{}_{}_'.format(TypeShot.LEVEL.name, LevelShot.EYE.name),
                                            disabled=True),
                                  sg.Text(LevelShot.EYE.value)],
                                 [sg.Button(image_data=btn_red_base64,
                                            key='_BTN_SHOT_{}_{}_'.format(TypeShot.LEVEL.name, LevelShot.SHOULDER.name),
                                            disabled=True),
                                  sg.Text(LevelShot.SHOULDER.value)],
                                 [sg.Button(image_data=btn_red_base64,
                                            key='_BTN_SHOT_{}_{}_'.format(TypeShot.LEVEL.name, LevelShot.HIP.name),
                                            disabled=True),
                                  sg.Text(LevelShot.HIP.value)],
                                 [sg.Button(image_data=btn_red_base64,
                                            key='_BTN_SHOT_{}_{}_'.format(TypeShot.LEVEL.name, LevelShot.KNEE.name),
                                            disabled=True),
                                  sg.Text(LevelShot.KNEE.value)],
                                 [sg.Button(image_data=btn_red_base64,
                                            key='_BTN_SHOT_{}_{}_'.format(TypeShot.LEVEL.name, LevelShot.GROUND.name),
                                            disabled=True),
                                  sg.Text(LevelShot.GROUND.value)],
                             ], element_justification='l', title_location=sg.TITLE_LOCATION_TOP,
                             key='_FRAME_{}_BUTTONS_'.format(TypeShot.LEVEL.name))
"""

layout_feature_annotator = [
    sg.Column([[layout_angle_view]], element_justification='c'),
    sg.Column(layout_frames_extract_shot_view, element_justification='c'),
    sg.Column([[layout_level_view]], element_justification='c'),
]

# -------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------

layout_table = [
    sg.Column([[sg.Save("Save annotations to CSV", key="_BTN_SAVE_CSV_", disabled=True)]], element_justification='r',
              expand_x=True, expand_y=True),
]

# -------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------

layout_window = [[
    sg.Column(layout_videoplayer_options, element_justification='c', expand_x=True, expand_y=True),
    sg.VerticalSeparator(),
    sg.Column([layout_feature_annotator, layout_table], element_justification='c', expand_x=True, expand_y=True),
]]


# "_BTN_{ANGLE|LEVEL|SCALE}_{*}" -> .update(disabled=True)

def reset_red_all_btn(element: typing.Any) -> None:
    if isinstance(element, list):
        for list_elem in element:
            reset_red_all_btn(list_elem)
    elif 'Rows' in element.__dir__():
        reset_red_all_btn(element.Rows)
    elif isinstance(element, sg.Button):
        element.update(image_data=btn_red_base64)


def commute_btn(button: sg.Button, pressed: bool) -> bool:
    if pressed:
        button.update(image_data=btn_green_base64)
        return False
    else:
        button.update(image_data=btn_red_base64)
        return False


def disable_element(element: typing.Any, disable: bool) -> None:
    if isinstance(element, list):
        for list_elem in element:
            disable_element(list_elem, disable)
    elif 'Rows' in element.__dir__():
        disable_element(element.Rows, disable)
    elif isinstance(element, (sg.Button, sg.Checkbox, sg.Slider, sg.Spin)):
        element.update(disabled=disable)


def reset_buttons(element: typing.Any):
    if isinstance(element, list):
        for list_elem in element:
            return reset_buttons(list_elem)
    elif 'Rows' in element.__dir__():
        return reset_buttons(element.Rows)
    elif isinstance(element, sg.Button):
        element.update(disabled=True)
