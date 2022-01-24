import PySimpleGUI as sg
import os.path
from datetime import time

from control.VideoPlayerThread import VideoPlayerExtractor
from control.util import convert_millisec_to_timeobj
from control.default_values import *
from view.Layers import layout_window

from predictor_net.Predictor import PredictorNet
from view.Layers import disable_element, reset_red_all_btn, commute_btn
from model.TypeShots import TypeShot, AngleShot, LevelShot, ScaleShot

from model.ReportDataframe import PATH_SAVE_CSV


class ViewGenerator:

    def __init__(self) -> None:
        self.main_window = sg.Window('Demo Feature extractor and annotator', layout_window, resizable=True)
        self.predictor = PredictorNet()
        self.dict_settings_video = {
            KEYDICT_PATH_FILE: '',
            KEYDICT_PATH_CSV: '',
            KEYDICT_DELTA_FRAME: default_delta_frames,
            KEYDICT_CHECKBOX_ANGLE_: default_checkbox_angle,
            KEYDICT_CHECKBOX_LEVEL_: default_checkbox_level,
            KEYDICT_CHECKBOX_SCALE_: default_checkbox_scale
        }
        self.video_player_thread = None
        self._init_predictor()

    def _init_predictor(self) -> None:
        messageBox = sg.Window("Loading", [[sg.Text("Loading models.\nPlease wait!")]], modal=True, no_titlebar=True)
        messageBox.read(timeout=1)
        self.predictor.load_predictors()
        messageBox.close()
        sg.popup(self.predictor.str_predictors_loaded(), non_blocking=True, keep_on_top=True)

    def close_view(self) -> None:
        self.main_window.close()

    def event_view_checking(self) -> None:
        while True:
            event, values = self.main_window.read()
            # Close window event
            if event == "Exit" or event == sg.WIN_CLOSED:
                break
            # Load video event
            elif event == "_FILEBROWSE_":
                if self.video_player_thread:
                    self.video_player_thread.signal_stop_thread()
                pathFile = values[event]
                if pathFile == '':
                    msg = "Please select a video"
                    self.dict_settings_video[KEYDICT_PATH_FILE] = ''
                    self.main_window['_BTN_LOAD_VIDEO_'].update(disabled=True)
                else:
                    if os.path.isfile(pathFile):
                        msg = "Video found: {}".format(pathFile.split('/')[-1])
                        self.dict_settings_video[KEYDICT_PATH_FILE] = pathFile
                        self.main_window['_BTN_LOAD_VIDEO_'].update(disabled=False)
                    else:
                        msg = "Video does not exist"
                        self.dict_settings_video[KEYDICT_PATH_FILE] = ''
                        self.main_window['_BTN_LOAD_VIDEO_'].update(disabled=True)
                self.main_window['_FILEBROWSE_TEXT_'].update(msg)
            elif '_CHECKBOX_' in event:
                if 'ANGLE' in event:
                    self.dict_settings_video[KEYDICT_CHECKBOX_ANGLE_] = values[event]
                elif 'LEVEL' in event:
                    self.dict_settings_video[KEYDICT_CHECKBOX_LEVEL_] = values[event]
                elif 'SCALE' in event:
                    self.dict_settings_video[KEYDICT_CHECKBOX_SCALE_] = values[event]
            elif event == '_RATIO_FRAMES_CAPTURE_':
                self.dict_settings_video[KEYDICT_DELTA_FRAME] = values[event]
            elif event == '_BTN_LOAD_CSV_':
                pathFile = values[event]
                if pathFile == '':
                    msg = "Please select a CSV file"
                    self.dict_settings_video[KEYDICT_PATH_CSV] = ''
                else:
                    if os.path.isfile(pathFile):
                        msg = "CSV found: {}".format(pathFile.split('/')[-1])
                        self.dict_settings_video[KEYDICT_PATH_CSV] = pathFile
                    else:
                        msg = "CSV does not exist"
                        self.dict_settings_video[KEYDICT_PATH_CSV] = ''
                self.main_window['_TXT_CSV_LOADED_'].update(msg)

            elif event == '_BTN_LOAD_VIDEO_':
                disable_element(self.main_window['_COLUMN_SETTINGS_'], True)
                self.main_window['_BTN_LOAD_VIDEO_'].update(disabled=True)
                self.main_window['_BTN_RESET_VIDEO_'].update(disabled=False)
                # init daemon video player
                self.video_player_thread = VideoPlayerExtractor(self.main_window, self.predictor, self.dict_settings_video)
                # Upgrade progress_bar
                self.init_progress_bar(self.video_player_thread.limit_frames[1], round(self.video_player_thread.duration_movie_second * 1000))
                # Setting predictor
                self.predictor.active_predictions_from_dict(self.dict_settings_video)
                # Start thread
                self.video_player_thread.start()
                disable_element(self.main_window['_CONTROL_GROUP_BTN_'], False)
                self.main_window['_BTN_SAVE_CSV_'].update(disabled=False)

            if self.video_player_thread:
                if event == '_BTN_RESET_VIDEO_':
                    res = sg.popup_ok_cancel("Do you want to reset everything? All work done will be lost.")
                    if res == 'OK':
                        # Stop thread (automatically delete the report)
                        if self.video_player_thread:
                            self.video_player_thread.signal_stop_thread()
                            self.video_player_thread = None
                        # Reset progress_bar
                        self.total_reset_progress_bar()
                        # reset video frames
                        self.main_window["_IMAGE_VIDEOPLAYER_"].update(data='', size=size_videoplayer_frame)
                        self.main_window["_IMAGE_ANNOTATION_"].update(data='', size=size_annotation_frame)
                        # unlock column settings
                        disable_element(self.main_window['_COLUMN_SETTINGS_'], False)
                        self.main_window['_BTN_RESET_VIDEO_'].update(disabled=True)
                        self.main_window['_BTN_LOAD_VIDEO_'].update(disabled=False)
                        self.main_window['_PLAY_PAUSE_BUTTON_'].update('Play')
                        disable_element(self.main_window['_CONTROL_GROUP_BTN_'], True)
                        self.main_window['_BTN_SAVE_CSV_'].update(disabled=True)
                        reset_red_all_btn(self.main_window[f'_FRAME_{TypeShot.ANGLE.name}_BUTTONS_'])
                        reset_red_all_btn(self.main_window[f'_FRAME_{TypeShot.LEVEL.name}_BUTTONS_'])
                        reset_red_all_btn(self.main_window[f'_FRAME_{TypeShot.SCALE.name}_BUTTONS_'])
                        # Clear selections:
                        self.main_window['_FILEBROWSE_'].update("")
                        self.main_window['_FILEBROWSE_TEXT_'].update("Please select a video file")
                        self.main_window['_RATIO_FRAMES_CAPTURE_'].update(default_delta_frames)
                        self.main_window['_BTN_LOAD_CSV_'].update("")
                        self.main_window['_TXT_CSV_LOADED_'].update("Please select a CSV file")
                        # reset dictionary
                        self.dict_settings_video[KEYDICT_PATH_FILE] = ''
                        self.dict_settings_video[KEYDICT_PATH_CSV] = ''
                        self.dict_settings_video[KEYDICT_DELTA_FRAME] = default_delta_frames
                        # disable feature buttons
                        self.unlock_features_buttons(False)

                elif event == '_BACKWARD_DELTA_FRAME_BUTTON_':
                    self.video_player_thread.backward_step_frame(delta=True)

                elif event == '_BACKWARD_ONE_FRAME_BUTTON_':
                    self.video_player_thread.backward_step_frame()

                elif event == '_FORWARD_DELTA_FRAME_BUTTON_':
                    self.video_player_thread.forward_step_frame(delta=True)

                elif event == '_FORWARD_ONE_FRAME_BUTTON_':
                    self.video_player_thread.forward_step_frame()

                elif event == '_BTN_MANUAL_EXTRACTION_':
                    self.video_player_thread.manual_prediction()

                elif event == '_PLAY_PAUSE_BUTTON_':
                    self.video_player_thread.commute_play_pause()
                    if self.video_player_thread.play:
                        # dsable *ward buttons
                        self.main_window['_PLAY_PAUSE_BUTTON_'].update('Pause')
                        self.main_window['_BACKWARD_DELTA_FRAME_BUTTON_'].update(disabled=True)
                        self.main_window['_BACKWARD_ONE_FRAME_BUTTON_'].update(disabled=True)
                        self.main_window['_FORWARD_ONE_FRAME_BUTTON_'].update(disabled=True)
                        self.main_window['_FORWARD_DELTA_FRAME_BUTTON_'].update(disabled=True)
                        self.main_window['_BTN_SAVE_CSV_'].update(disabled=True)
                        self.main_window['_BTN_MANUAL_EXTRACTION_'].update(disabled=True)
                        # disable feature buttons
                        self.unlock_features_buttons(False)
                    else:
                        # enable *ward buttons
                        self.main_window['_PLAY_PAUSE_BUTTON_'].update('Play')
                        self.main_window['_BACKWARD_DELTA_FRAME_BUTTON_'].update(disabled=False)
                        self.main_window['_BACKWARD_ONE_FRAME_BUTTON_'].update(disabled=False)
                        self.main_window['_FORWARD_ONE_FRAME_BUTTON_'].update(disabled=False)
                        self.main_window['_FORWARD_DELTA_FRAME_BUTTON_'].update(disabled=False)
                        self.main_window['_BTN_SAVE_CSV_'].update(disabled=False)
                        self.main_window['_BTN_MANUAL_EXTRACTION_'].update(disabled=False)
                        # enable feature buttons
                        self.unlock_features_buttons(True)

                # '_BTN_SHOT_{}_{}_'.format(TypeShot.LEVEL.name, LevelShot.KNEE.name)
                # Save feature
                # When button is clicked!
                elif '_BTN_SHOT_' in event:
                    feature_val = event.split('_')[-2]
                    if f'{TypeShot.ANGLE.name}' in event:
                        type_shot = TypeShot.ANGLE
                        ann = AngleShot[feature_val]
                    elif f'{TypeShot.LEVEL.name}' in event:
                        type_shot = TypeShot.LEVEL
                        ann = LevelShot[feature_val]
                    elif f'{TypeShot.SCALE.name}' in event:
                        type_shot = TypeShot.SCALE
                        ann = ScaleShot[feature_val]
                    else:
                        break
                    # reset bottons
                    reset_red_all_btn(self.main_window[f'_FRAME_{type_shot.name}_BUTTONS_'])

                    # Pulsante <- JoinTypeShot se in dict era None, altrimenti ann.
                    # Controlla se premo lo stesso pulsante
                    previous_value = self.video_player_thread.dict_features[type_shot]

                    # Se ripremo lo stesso pulsante, oppure se ne premo un altro
                    self.video_player_thread.dict_features[type_shot] = ann if previous_value is None or previous_value is not ann else None
                    # commute the choiced button
                    commute_btn(self.main_window[event], True if previous_value is None or previous_value is not ann else False)

                    # Save the row
                    self.video_player_thread.save_state_feat_dict_in_report(type_shot)

                elif event == '_BTN_SAVE_CSV_':
                    is_save = self.video_player_thread.report.save_to_csv()
                    if is_save:
                        sg.popup(f"Annotations saved in folder: {PATH_SAVE_CSV}", non_blocking=True, keep_on_top=True)
        self.close_view()

    def init_progress_bar(self, total_frame: int, total_millisec: int) -> None:
        self.main_window['_PROGRESS_BAR_VIDEO_'].update(current_count=0, max=total_frame)
        n_frame, timer = total_frame + 1, convert_millisec_to_timeobj(total_millisec)
        self.main_window['_TOTAL_TIME_FRAME_PROGRESS_BAR_'].update(f"{timer: %M:%S} / {n_frame: 04d}")
        self.reset_progress_bar()

    def reset_progress_bar(self) -> None:
        n_frame, zerotime = 0 + 1, time(second=0)
        self.main_window['_TIME_FRAME_PROGRESS_BAR_'].update(f"{zerotime: %M:%S} / {n_frame: 04d}")

    def total_reset_progress_bar(self) -> None:
        n_frame, zerotime = 0, time(second=0)
        self.main_window['_PROGRESS_BAR_VIDEO_'].update(current_count=0, max=100)
        self.main_window['_TIME_FRAME_PROGRESS_BAR_'].update(f"{zerotime: %M:%S} / {n_frame: 04d}")
        self.main_window['_TOTAL_TIME_FRAME_PROGRESS_BAR_'].update(f"{zerotime: %M:%S} / {n_frame: 04d}")

    def unlock_features_buttons(self, unlock: bool) -> None:
        if self.dict_settings_video[KEYDICT_CHECKBOX_ANGLE_]:
            disable_element(self.main_window[f'_FRAME_{TypeShot.ANGLE.name}_BUTTONS_'], not unlock)
        if self.dict_settings_video[KEYDICT_CHECKBOX_LEVEL_]:
            disable_element(self.main_window[f'_FRAME_{TypeShot.LEVEL.name}_BUTTONS_'], not unlock)
        if self.dict_settings_video[KEYDICT_CHECKBOX_SCALE_]:
            disable_element(self.main_window[f'_FRAME_{TypeShot.SCALE.name}_BUTTONS_'], not unlock)

