import os
import cv2
import numpy as np
from keras.models import load_model
from typing import Dict
from model.TypeShots import AngleShot, LevelShot, ScaleShot, JoinTypeShots, TypeShot
from control.default_values import *

from tensorflow.keras.applications.resnet50 import preprocess_input as preprocess_resnet50

# Name_model = (name_file, preprocessor_ref, dim_image_input, ordered_reference_output-shot, type-camera-feature)

MODEL_ANGLE = ("model_angle_256", preprocess_resnet50, (256, 256), [AngleShot.DUTCH, AngleShot.HIGH, AngleShot.LOW,
                                                                    AngleShot.NOANGLE, AngleShot.OVERHEAD],
               TypeShot.ANGLE)
MODEL_LEVEL = ("model_level_256", preprocess_resnet50, (256, 256), [LevelShot.AERIAL, LevelShot.EYE, LevelShot.HIP,
                                                                    LevelShot.KNEE, LevelShot.SHOULDER,
                                                                    LevelShot.GROUND],
               TypeShot.LEVEL)
MODEL_SCALE = ("model_scale_256", preprocess_resnet50, (256, 256), [ScaleShot.CLOSE, ScaleShot.LONG, ScaleShot.MEDIUM],
               TypeShot.SCALE)


def preprocessing(frame_byte: np.ndarray, size_tuple: (int, int), preprocessor) -> np.array:
    """
    Preprocessing:
        1 - resize
        2 - convert to Numpy Array
    :param frame_byte: Numpy Array of the image
    :param size_tuple: (width, height) of the resizing
    :param preprocessor: preprocessor. Definded by the CNN of the model.
    :return: Numpy Array of the image
    """
    # resize frame
    frame_resize = cv2.resize(frame_byte, size_tuple, interpolation=cv2.INTER_LINEAR)
    # image -> numpy array
    frame_array = np.asarray(frame_resize, dtype='int')
    # preprocessors
    return preprocessor(frame_array)


class PredictorNet:
    def __init__(self) -> None:
        self.model_predictors = {}
        self.active_angle, self.active_level, self.active_scale = \
            default_checkbox_angle, default_checkbox_level, default_checkbox_scale

    def make_prediction(self, data_frame: np.ndarray) -> Dict[TypeShot, JoinTypeShots]:
        """
        Generate predictions from predictors choiced by Checkboxes in View
        :param data_frame: Image in format Numpy Array, previously preprocessed.
        :return: Dictionary with key TypeShot enum and value AngleShots, LevelShots or ScaleShots
        """
        predictions = {}
        for name, predictor in self.model_predictors.items():
            if name is TypeShot.ANGLE and self.active_angle or name is TypeShot.LEVEL and self.active_level or \
                    name is TypeShot.SCALE and self.active_scale:
                frame_preprocessed = preprocessing(data_frame, predictor[2], predictor[1]) \
                    .reshape((1, predictor[2][0], predictor[2][1], 3))
                results = predictor[0].predict(frame_preprocessed).argmax(axis=1)
                predictions[name] = predictor[3][results[0]]
        return predictions

    def load_predictors(self) -> bool:
        """
        Method to call for load model from folder 'models/
        :return: True if all models are loaded correctly, False otherwise (if just one model are not correctly loaded)
        """
        correct_load_check = True

        dirname = os.getcwd()  # os.path.dirname(__file__)
        model_angle_file = os.path.join(dirname, 'models/' + MODEL_ANGLE[0])
        model_level_file = os.path.join(dirname, 'models/' + MODEL_LEVEL[0])
        model_scale_file = os.path.join(dirname, 'models/' + MODEL_SCALE[0])

        for model_file in [[model_angle_file, *MODEL_ANGLE[1:]],
                           [model_level_file, *MODEL_LEVEL[1:]],
                           [model_scale_file, *MODEL_SCALE[1:]]]:
            try:
                if os.path.isdir(model_file[0]):
                    type_cf = model_file[4]
                    self.model_predictors[type_cf] = (load_model(model_file[0], compile=False), model_file[1],
                                                      model_file[2], model_file[3])
                    # check if model is correct, else remove
                    model_output = self.model_predictors[type_cf][0].layers[-1].output.shape[1]
                    expected_output = len(model_file[3])
                    if model_output != expected_output:
                        print(f"Problem model {model_file[0]}: expected {expected_output} output neurons;"
                              f"actually {model_output} output neurons; Remove model!")
                        correct_load_check = False
                        self.model_predictors.pop(type_cf)
                    else:
                        print(f"Model {model_file[0]} correctly loaded!")

            except IOError as e:
                print(f"Error load model {model_file[0]}.\n{e}")
                correct_load_check = False
        """try:
            # load model Angle features
            if os.path.isdir(model_angle_file):
                self.model_predictors[TypeShot.ANGLE] = (load_model(model_angle_file, compile=False), MODEL_ANGLE[1],
                                                         MODEL_ANGLE[2], MODEL_ANGLE[3])
                # check if model is correct, if not remove
                if self.model_predictors[TypeShot.ANGLE][0].layers[-1].output.shape[1] != len(MODEL_ANGLE[3]):
                    self.model_predictors.pop(TypeShot.ANGLE)

            # load model Level features
            if os.path.isdir(model_level_file):
                self.model_predictors[TypeShot.LEVEL] = (load_model(model_level_file, compile=False), MODEL_LEVEL[1],
                                                         MODEL_LEVEL[2], MODEL_LEVEL[3])
                # check if model is correct, if not remove
                if self.model_predictors[TypeShot.LEVEL][0].layers[-1].output.shape[1] != len(MODEL_LEVEL[3]):
                    self.model_predictors.pop(TypeShot.LEVEL)

            # load model Scale features
            if os.path.isdir(model_scale_file):
                self.model_predictors[TypeShot.SCALE] = (load_model(model_scale_file, compile=False), MODEL_SCALE[1],
                                                         MODEL_SCALE[2], MODEL_SCALE[3])
                # check if model is correct, if not remove
                if self.model_predictors[TypeShot.SCALE][0].layers[-1].output.shape[1] != len(MODEL_SCALE[3]):
                    self.model_predictors.pop(TypeShot.SCALE)
            return True

        except IOError as e:
            print(f"Error load model!\n{e}")
            return False"""
        return correct_load_check

    def str_predictors_loaded(self) -> str:
        """
        Method to print a message. How many and which models are loaded.
        :return: string with a message.
        """
        len_mod = len(self.model_predictors)
        if len_mod > 0:
            message = f"Loaded {len_mod} models:\n"
            message += f"{', '.join([name.value for name, _ in self.model_predictors.items()])}."
        else:
            message = f"No model found in folder 'models/'."
        return message

    def active_predictions_from_dict(self, dict_predictions: Dict[str, bool]) -> None:
        """
        Set which predictors use in prediction
        :param dict_predictions: a dictionary with key: KEYDICT_CHECKBOX_{}_ in control/default_values.py and value bool
        :return: None
        """
        self.active_angle = dict_predictions[KEYDICT_CHECKBOX_ANGLE_]
        self.active_level = dict_predictions[KEYDICT_CHECKBOX_LEVEL_]
        self.active_scale = dict_predictions[KEYDICT_CHECKBOX_SCALE_]
