# AniXtract: camera-feature extraction, classification and annotation tool

## Python dependencies
 - PySimpleGUI
 - Pillow
 - opencv-python
 - pafy (Comment from April 2022: `pafy` has not been updated since YouTube changed the standard `Dislike` behaviour, preventing the module from running correctly: to fix this, you need to edit the code of the `pafy` module: comment/remove line 54 of file `backend_youtube_dl.py` (`self._dislikes = self._ydl_info[ dislike_count']`).)
 - youtube-dl
 - pandas
 - keras and tensorflow (2.6.0, read below)

## Instructions
 - Place the Keras models in the `/models` folder. They will be recognised automatically on start-up.
 - The programme is available in the form of executable releases under Microsoft or Linux: simply run the respective executables. Alternatively, to use the source code directly, you need to install the dependencies listed above and run `python main.py`.
 - In the area at the top left, select the film to be analysed: you can choose a local file (accepted formats `.mkv` and `.mp4`) or a film from YouTube by typing in the full URL. Then select the camera-features to be extracted automatically with the models and the extraction frequency, from 1 to 7 seconds between two frames, then click on `Load video and settings`. If necessary, also load the csv file.
 - Once the video has been loaded, in the lower left-hand area you can see the position of the extractor in the film (number of frames and minutes).
 - At the top right are the controls for the video. Click on `Play` to start the automatic extraction. Click on `Pause` to pause.
 Click on `<` or `>` to scroll backwards or forwards one frame at a time, or `<<` or `>>` to skip a number of frames equal to the draw frequency.
 of frames equal to the extraction frequency.
 - Click on `Call model prediction` to force a model prediction on the frame.
 - Annotation buttons are located on the edges of the screen. At the chosen frame, click on the button corresponding to the chosen annotation. Reclick
 the button to cancel the choice made.
 - Click on `Save annotation to CSV` to save the annotation up to that moment in a `.csv` file.

## Download Keras models
The models can be found at: https://cinescale.github.io/anime/#get-the-model (alternative link: https://drive.google.com/drive/folders/13LYHyYeakSYc0NaxqSCbMR5qOSOVWnxB?usp=sharing). These models work with version 2.6.0 of Tensorflow and Keras.

Download the models and place them in the `/models` folder.

## Extra: use `yt-dlp` instead of `youtube-dl`
`yt-dlp` is a fork of `youtube-dl` with new features and patches (https://github.com/yt-dlp/yt-dlp). To use the source code with `yt-dlp` you have to edit the source code of the module `pafy`:
 - In file `pafy.py`:
   - row 48 -> import yt_dlp as youtube_dl
   - row 49 -> backend = "yt-dlp"  #"youtube-dl"
   - row 52 -> Change the string message if you want.
 - In file `backend_youtube_dl.py`:
   - row 13 -> import yt_dlp as youtube_dl
Finally, download the Python module `yt-dlp`.
