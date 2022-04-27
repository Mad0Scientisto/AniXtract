class Error(Exception):
    """
    Main class for exceptions
    """
    pass


# Exceptions for VideoPlayerThread.py
class TransferInfoError(Error):
    """
    Exceptions raised when during __init__ in VideoPlayerThread the dictionary "parameter" have the two field
    KEYDICT_YT_URL and KEYDICT_PATH_FILE empty.
    """

    def __str__(self):
        return "The dictionary 'parameter' have the two field 'KEYDICT_YT_URL' and 'KEYDICT_PATH_FILE' empty."


class OpeningFileError(Error):
    """
    Exceptions raised when during __init__ the source had problems during the opening.
    """

    def __str__(self):
        return "The source had problems during the opening."


class GenericOpenCVError(Error):
    """
    Exceptions raised with a generic error of module OpenCV. Make to capture an exception 'cv2.error'.
    """
    def __init__(self, exception):
        self.exception = exception

    def __str__(self):
        return f"The source had problems during the opening.\n{self.exception}"
