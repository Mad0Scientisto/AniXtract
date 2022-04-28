from datetime import time

NAME_MAIN_WINDOW = "AniXtract: Feature extractor and annotator"

# All messages in application
MSG_LOADING_MODELS = "Loading models.\nPlease wait!"

MSG_SELECT_VIDEO_FILE = "Please select a video file"
MSG_DIGIT_YOUTUBE_URL = "Please digit a valid YouTube URL"

MSG_SELECT_VIDEO_FILE_OK = "Video found: {}"
MSG_SELECT_VIDEO_FILE_FAIL = "Video does not exist"

MSG_DIGIT_YOUTUBE_URL_OK = "URL Valid"
MSG_DIGIT_YOUTUBE_URL_FAIL = "URL not valid"

MSG_SELECT_CSV_FILE = "Please select a CSV file"
MSG_SELECT_CSV_FILE_OK = "CSV found: {}"
MSG_SELECT_CSV_FILE_NE = "CSV does not exist"
MSG_SELECT_CSV_FILE_FAIL = "CSV badly formatted"

MSG_POPUP_RESET_EXTRACTION = "Do you want to reset everything? All work done will be lost."

MSG_SAVE_CSV_ANNOTATION = "Annotations saved in folder: {}"

MSG_PRED_LOADED_MODEL = "Loaded {} models:\n{}."
MSG_PRED_NO_MODELS = "No model found in folder '{}'."

# Text inside an Input area
TXT_INPUT_VOID_VIDEO_FILE = ''
TXT_INPUT_VOID_URL_YOUTUBE = ''
TXT_INPUT_VOID_CSV_FILE = ''

# Other
NAME_WINDOW_LOADING_MODELS = "Loading"
NAME_FRAME_SELECT_SRC = 'Select source'
NAME_FRAME_SELECT_CAMERA_FEATURES = 'Select camera features to extract'
NAME_FRAME_SELECT_FREQUENCY_EXTRACTION = 'Frames extraction frequency'
NAME_FRAME_SELECT_CSV_PREV_ANNOTATION = 'Load annotations from CSV file'

# Text Buttons, Radio, Spin
TXT_BTN_LOAD_VIDEO_FILE = "Load"
TXT_BTN_LOAD_CSV_PREV_ANNOTATION = "Load from CSV file"

TXT_RADIO_FILE_SRC = 'Load video'
TXT_RADIO_YOUTUBE_SRC = 'YouTube URL'

TXT_PRE_SPIN_FREQ_CAPTURE = "Capture 1 frame every "
TXT_POST_SPIN_FREQ_CAPTURE = " seconds"

TXT_BTN_LOAD_VIDEO_SET = "Load video and settings"
TXT_BTN_RESET_VIDEO_SET = "Reset"

TXT_BTN_CLEAR_INPUT = "Clear"

TXT_BTN_PLAY = 'Play'
TXT_BTN_PAUSE = 'Pause'
TXT_BTN_BW_DELTA = "<<"
TXT_BTN_BW_ONE = "<"
TXT_BTN_FW_DELTA = ">>"
TXT_BTN_FW_ONE = ">"

TXT_BTN_MANUAL_PRED = "Call model prediction"

TXT_BTN_SAVE_ANNOTATION = "Save annotations to CSV"

# Error messages
ERROR_MSG_LOADING_DAEMON_VIDEO_PLAYER = "Error while loading the source:\n{}"
ERROR_MSG_CSV_BADLY_FORMATTED = "Error: CSV badly formatted.\nCSV file not loaded."


# Formatting strings
def string_formatted_time_frame(timer: time, n_frame: int) -> str:
    return f"{timer:%M:%S} / {n_frame:04d}"


def zf_time_frame():
    return string_formatted_time_frame(time(0), 0)


def string_num_frame_video(n_frame: int) -> str:
    return f"Frame: {n_frame:04d}"
