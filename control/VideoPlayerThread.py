import logging
import typing

import cv2
import threading
import time
import numpy as np
from typing import Optional, Tuple, Dict, Any

from predictor_net.Predictor import PredictorNet
from view import viewGenerator
from PySimpleGUI import Window
from control.util import convert_millisec_to_timeobj
from view.Layers import size_videoplayer_frame, size_annotation_frame
from view.Layers import disable_element, reset_red_all_btn, commute_btn
from model.TypeShots import TypeShot, AngleShot, LevelShot, ScaleShot, JoinTypeShots
from control.default_values import *
from model.ReportDataframe import ReportAnnotationFilm

from control.exceptions import TransferInfoError, GenericOpenCVError, OpeningFileError

import control.strings as strfile

import pafy


class VideoPlayerExtractor(threading.Thread):

    def __init__(self, ref_main_view: viewGenerator, predictor: PredictorNet, parameter: Dict[str, Any]) -> None:
        """
        Init the thread
        :param window: Window object, from PySimpleGui
        :param predictor: Predictor inited
        :param parameter: dictionary of parameters
        """
        # calling parent class constructor
        threading.Thread.__init__(self, daemon=True)
        self.ref_main_view = ref_main_view
        self.window = self.ref_main_view.main_window

        try:
            if parameter[KEYDICT_PATH_FILE]:
                self.path_file = parameter[KEYDICT_PATH_FILE]

                # Load video
                self.video = cv2.VideoCapture(self.path_file)

                # Name file
                self.name_file = self.path_file.split('/')[-1]
            elif parameter[KEYDICT_YT_URL]:
                self.url_youtube = parameter[KEYDICT_YT_URL]
                self.video_youtube_metadata = pafy.new(self.url_youtube)
                self.video_youtube_stream = self.video_youtube_metadata.getbest(preftype="mp4")

                # Load video
                self.video = cv2.VideoCapture(self.video_youtube_stream.url)

                # Name file
                self.name_file = f"{self.video_youtube_metadata.title} --- {self.video_youtube_metadata.watchv_url}"
            else:
                raise TransferInfoError
            if not self.video.isOpened():
                raise OpeningFileError
        except cv2.error as e:
            raise GenericOpenCVError(e)

        # Get information from video: FPS, duration in seconds, total frame, border(first frame, last_frame),
        self.fps = round(self.video.get(cv2.CAP_PROP_FPS))  # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
        self.total_movie_frame = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.limit_frames = (0, self.total_movie_frame - 1)
        self.duration_movie_second = (self.total_movie_frame / self.fps)  # - (1/self.fps)  # Remove 1 frame

        # Calculate delta frame (how many frames jump to next/previous frame)
        delta_frames = parameter[
            KEYDICT_DELTA_FRAME] if KEYDICT_DELTA_FRAME in parameter.keys() else default_delta_frames
        self.delta_frames = self.fps * delta_frames

        # Define dictionary for every features. Dict of Dict {Type.ANGLE: AngleShot or None, ...}}
        self.dict_features = {
            TypeShot.ANGLE: None,
            TypeShot.LEVEL: None,
            TypeShot.SCALE: None
        }

        # Boolean to check if play or pause
        self.play = False
        # Boolean to check if movie is finished (last frame)
        self.finish_video = False

        # Value to define the "state" of the video player: actual frame, last frame captured for predictor and last
        #  row find in report
        self.last_frame_captured = 0
        self.last_row_in_report_finded = (None, None)
        self.counter_frames = 0
        self.array_last_frame_captured = None

        # New Report and the predictor
        self.report = ReportAnnotationFilm(self.name_file)
        self.predictor = predictor

        # load csv
        if parameter[KEYDICT_PATH_CSV] != '':
            is_loaded = self.report.load_csv_from_file(parameter[KEYDICT_PATH_CSV])
            if not is_loaded:
                # TODO: Out of domain!?
                import PySimpleGUI as sg
                sg.popup(strfile.ERROR_MSG_CSV_BADLY_FORMATTED, non_blocking=True, keep_on_top=True)
                self.window['_TXT_CSV_LOADED_'].update(strfile.MSG_SELECT_CSV_FILE_FAIL)

        # Show first frame
        success_reading, frame = self.video.read()
        self.print_videoplayer(frame)
        self.print_frame_captured(frame, self.last_frame_captured)

        # Signal to kill thread
        self._signal_stop = False

    def run(self) -> None:
        """
        Run the thread. Pseudoalg.
            while not kill_signal:
                time.sleep() to allow near real playback speed.
                if play_btn:
                    capture_frame
                    if end_video:
                    force pause, unlock all buttons, upgrade progress_bar
            ^-----------continue

                    Show frame, upgrade counter frame and progress bar
                    if counter frame % delta == 0:
                        upgrade last_frame_counter
                        check if this frame is in report
                            if True, load old prediction
                            else, call predictor to make new prediction
                            add prediction to report.
                        Manage color buttons in view
                        print frame captured
            if exit from while, stop window view
        :return: None
        """
        # Read until video is completed; can press pause
        delta_time = 0
        while not self._signal_stop:
            # Calculate delta for speed video
            ts = (1 / self.fps - time.time() + delta_time)
            if delta_time > 0 and not ts < 0:
                time.sleep(ts)
            delta_time = time.time()

            # If play is pressed, show and capture
            if self.play:
                success_reading, frame = self.video.read()
                if not success_reading:
                    self.set_play_video(False)
                    self.update_progress_bar()
                    self.window['_PLAY_PAUSE_BUTTON_'].update('Stop')
                    self.window['_BACKWARD_DELTA_FRAME_BUTTON_'].update(disabled=False)
                    self.window['_BACKWARD_ONE_FRAME_BUTTON_'].update(disabled=False)
                    self.window['_FORWARD_ONE_FRAME_BUTTON_'].update(disabled=False)
                    self.window['_FORWARD_DELTA_FRAME_BUTTON_'].update(disabled=False)
                    self.window['_BTN_MANUAL_EXTRACTION_'].update(disabled=False)
                    # unlock features button
                    self.ref_main_view.unlock_features_buttons(True)
                    continue
                try:
                    assert type(frame) is np.ndarray
                except AssertionError:
                    break
                self.counter_frames += 1
                # Show frame in video player
                self.print_videoplayer(frame)
                self.update_progress_bar()

                # Capture frame condition
                if self.counter_frames % self.delta_frames == 0:
                    # Print frame with value
                    self.last_frame_captured = self.counter_frames
                    self.array_last_frame_captured = frame
                    # Get prediction in report
                    self.last_row_in_report_finded = self.report.get_row(self.last_frame_captured)
                    if self.last_row_in_report_finded != (None, None):
                        _, prediction_report = self.last_row_in_report_finded
                        row = prediction_report
                    else:
                        # Predittore bloccante
                        result = self.predictor.make_prediction(frame)
                        # Add row to report
                        row = {}
                        for key_type, value_type in result.items():
                            # Write on report
                            self.report.add_shot_ann(self.last_frame_captured, key_type, value_type)
                            row[key_type] = value_type
                    self.set_feature_buttons_by_row(row)
                    logging.info(self.report.report)
                    # Print frame captured
                    self.print_frame_captured(frame, self.last_frame_captured)
        self.video.release()

    def manual_prediction(self) -> bool:
        if self.array_last_frame_captured is None:
            return False
        result = self.predictor.make_prediction(self.array_last_frame_captured)
        # Add row to report
        row = {}
        for key_type, value_type in result.items():
            # Write on report
            self.report.add_shot_ann(self.last_frame_captured, key_type, value_type)
            row[key_type] = value_type
        self.set_feature_buttons_by_row(row)
        return True

    def save_state_feat_dict_in_report(self, type_shot: TypeShot) -> bool:
        # find JoinTypeShot that is True
        joinTypeTrue = self.dict_features[type_shot]
        if joinTypeTrue is not None:
            self.last_row_in_report_finded = self.report.get_row(self.last_frame_captured)
            # if i find this row in report search:
            if self.last_row_in_report_finded != (None, None):
                index_report, row_report = self.last_row_in_report_finded
                return self.report.modify_shot_ann_indexes(index_report, type_shot, joinTypeTrue)
            else:
                return self.report.add_shot_ann(self.counter_frames, type_shot, joinTypeTrue)
        return False

    def modify_actual_row_report(self, type_shot: TypeShot, new_ann: JoinTypeShots) -> bool:
        # Upgrade dictionary
        self.dict_features[type_shot] = new_ann
        return self.report.modify_shot_ann_indexes(self.counter_frames, type_shot, new_ann)

    def _upgrade_dictionary_feature_by_row(self, row: Dict[TypeShot, JoinTypeShots], activate_btn=False) -> None:
        """
        Upgrade dictionary internal of features (self.dict_features) and buttons if activate_btn is True
        :param row: dictionary[TypeShot] = Angle/Level/ScaleShot
        :param activate_btn:
        :return: None
        """
        # key: TypeShot: angle,level,scale
        for type_shot, union_type_shot in row.items():
            # Set dictionary and buttons
            if isinstance(type_shot, TypeShot):
                self.dict_features[type_shot] = union_type_shot
                # Commute the button to True -> get green button
                if activate_btn:
                    commute_btn(self.window[f'_BTN_SHOT_{type_shot.name}_{union_type_shot.name}_'], True)

    def set_feature_buttons_by_row(self, row: Dict[TypeShot, JoinTypeShots]) -> None:
        """
        Reset all button -> get red button
        Upgrade dictionary internal of features (self.dict_features) and buttons
        :param row: dictionary[TypeShot] = Angle/Level/ScaleShot
        :return: None
        """
        for type_shot in TypeShot:
            reset_red_all_btn(self.window[f'_FRAME_{type_shot.name}_BUTTONS_'])
        return self._upgrade_dictionary_feature_by_row(row, activate_btn=True)

    def set_feature_buttons_by_number_frame(self, n_frame: int) -> None:
        """
        Reset all button -> get red button
        Find in report if exist row of n_frame frame and get if exist, else pass
        Upgrade dictionary internal of features (self.dict_features) and buttons
        :param n_frame: number of frame
        :return: None
        """
        for type_shot in TypeShot:
            reset_red_all_btn(self.window[f'_FRAME_{type_shot.name}_BUTTONS_'])
            self.dict_features = {
                TypeShot.ANGLE: None,
                TypeShot.LEVEL: None,
                TypeShot.SCALE: None
            }
        self.last_row_in_report_finded = self.report.get_row(n_frame)
        if self.last_row_in_report_finded != (None, None):
            _, row_report = self.last_row_in_report_finded
            self._upgrade_dictionary_feature_by_row(row_report, activate_btn=True)

    def print_frame_captured(self, frame: np.ndarray, frame_num: int) -> None:
        """
        Print frame in captured frame. Add number_frame in image
        :param frame_num: Number frame
        :param frame: Numpy array of frame
        :return: None
        """
        frame = cv2.resize(frame, size_annotation_frame, interpolation=cv2.INTER_LINEAR)
        label = strfile.string_num_frame_video(int(frame_num + 1))
        x1, y1, padding = 20, 20, 5
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)
        cv2.rectangle(frame, (x1 - padding, y1 - h - padding), (x1 + w + padding, y1 + padding), (0, 0, 0), -1)
        cv2.putText(frame, label, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        imgbytes = cv2.imencode(".png", frame)[1].tobytes()
        self.window["_IMAGE_ANNOTATION_"].update(data=imgbytes)

    def print_videoplayer(self, frame: np.ndarray) -> None:
        """
        Print frame in videoplayer
        :param frame: Numpy array of frame
        :return: None
        """
        frame = cv2.resize(frame, size_videoplayer_frame, interpolation=cv2.INTER_LINEAR)
        imgbytes = cv2.imencode(".png", frame)[1].tobytes()
        self.window["_IMAGE_VIDEOPLAYER_"].update(data=imgbytes)
        self.update_progress_bar()

    def update_progress_bar(self) -> None:
        """
        Upgrade the progress bar by value of current frame
        :return: None
        """
        value_frame, value_millisec = self.get_current_pos()
        value_frame, value_millisec = value_frame + 1, value_millisec + (1000 / self.fps)  # Add 1 frame to bar
        self.window['_PROGRESS_BAR_VIDEO_'].update(current_count=value_frame, max=self.limit_frames[1])
        n_frame, timer = value_frame, convert_millisec_to_timeobj(round(value_millisec))
        self.window['_TIME_FRAME_PROGRESS_BAR_'].update(strfile.string_formatted_time_frame(timer, int(n_frame)))

    def set_play_video(self, play: bool) -> None:
        self.play = play

    def commute_play_pause(self) -> None:
        self.set_play_video(not self.play)

    def signal_stop_thread(self) -> None:
        self._signal_stop = True

    def _goto_frame(self, num_frame: int) -> Tuple[bool, int]:
        limit_frames = self.limit_frames
        if num_frame < limit_frames[0]:
            self.video.set(cv2.CAP_PROP_POS_FRAMES, limit_frames[0])
            return False, limit_frames[0]
        elif num_frame > limit_frames[1]:
            self.video.set(cv2.CAP_PROP_POS_FRAMES, limit_frames[1])
            return False, limit_frames[1]
        self.video.set(cv2.CAP_PROP_POS_FRAMES, num_frame)
        self.window['_BTN_MANUAL_EXTRACTION_'].update(disabled=False)
        self.window['_PLAY_PAUSE_BUTTON_'].update(strfile.TXT_BTN_PLAY)
        return True, num_frame

    def forward_step_frame(self, delta=False) -> None:
        current_frame = self.last_frame_captured
        new_n_frame = current_frame + self.delta_frames if delta else current_frame + 1
        # new_frame = self.total_movie_frame if new_frame > self.total_movie_frame else new_frame
        out_limit, new_n_frame = self._goto_frame(new_n_frame)

        self.counter_frames, self.last_frame_captured = new_n_frame, new_n_frame
        _, frame = self.video.read()
        self.array_last_frame_captured = frame
        self.print_frame_captured(frame, new_n_frame)
        self.print_videoplayer(frame)
        self.set_feature_buttons_by_number_frame(new_n_frame)

    def backward_step_frame(self, delta=False) -> None:
        current_frame = self.last_frame_captured
        new_n_frame = current_frame - self.delta_frames if delta else current_frame - 1
        # new_frame = 0 if new_frame < 0 else new_frame
        out_limit, new_n_frame = self._goto_frame(new_n_frame)

        _, frame = self.video.read()
        self.array_last_frame_captured = frame
        self.counter_frames, self.last_frame_captured = new_n_frame, new_n_frame
        self.print_frame_captured(frame, new_n_frame)
        self.print_videoplayer(frame)
        self.set_feature_buttons_by_number_frame(new_n_frame)

    def get_current_pos(self) -> Tuple[float, float]:
        # When it reaches the final frame (passes self.limit_frames) the time returns 0.0
        # cv2.CAP_PROP_POS_FRAMES -> 'Answers How many frames have I drawn so far?'
        # return round(self.video.get(cv2.CAP_PROP_POS_FRAMES)), self.video.get(cv2.CAP_PROP_POS_MSEC)
        return round(self.counter_frames), (self.counter_frames / self.fps) * 1000
