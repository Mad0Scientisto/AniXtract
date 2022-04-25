KEYDICT_PATH_FILE = 'path_file'
KEYDICT_YT_URL = 'youtube_url'
KEYDICT_PATH_CSV = 'path_csv'
KEYDICT_DELTA_FRAME = 'delta_frames'
KEYDICT_CHECKBOX_ANGLE_ = 'checkbox_angle'
KEYDICT_CHECKBOX_LEVEL_ = 'checkbox_level'
KEYDICT_CHECKBOX_SCALE_ = 'checkbox_scale'

size_annotation_frame = (500, 500)
size_videoplayer_frame = (300, 300)  # (256, 256)

default_delta_frames = 1

default_checkbox_angle = True
default_checkbox_level = True
default_checkbox_scale = True
default_checkbox_type = True

default_dict_path_file = ''
default_dict_url_youtube = ''
default_dict_path_csv = ''

video_file_ext_supported = (('MP4 File', '*.mp4'), ('MKV File', '*.mkv'))
csv_ext = (("CSV File", "*.csv"),)

# Image to show when frame is void or disable. For black screen use void string ''.
void_frame_image = ''  # For data or filename in PySimpleGUI.Image()
