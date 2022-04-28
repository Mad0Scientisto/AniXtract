import pandas as pd
import csv
from bisect import bisect_right
from model.TypeShots import *
from typing import Tuple, Dict, Optional
import os.path
from pathlib import Path
from datetime import datetime

import logging

PATH_SAVE_CSV = str(Path(os.path.dirname(__file__)).parent.absolute())
FILE_SAVE_CSV = PATH_SAVE_CSV + "/report_movie_{}_{}.csv"

KEY_FRAME_NUM = 'Frame'


class ReportAnnotationFilm:
    """
    Class for generating and managing the film annotation report. Structure:
    ---------------
    | Title movie |
    ------------------------------------------------------
    | Number frame | Angle Shot | Level Shot | Scale Shot |
    ------------------------------------------------------
    
    text column
    ---------------------------------
    | frame | angle | level | scale |
    ---------------------------------

    report -> Dict[n_row] -> row_elem
    n_row -> Dict[TypeShot: JointTypeShots ...]

    """

    def __init__(self, name_movie: str) -> None:
        self.name_movie = name_movie
        self.report = []

    def get_row(self, n_frame: int) -> Tuple[Optional[int], Optional[Dict[TypeShot, JoinTypeShots]]]:
        """
        Method that returns a tuple (index, row) where "index" is the index of the table in which the row "row" is
        located, otherwise if nothing is found it returns a tuple (None. None).
        :param n_frame: number of frame in movie.
        :return: (None, None) if not find any row, else (index_in_report, row).
        """
        for index_row, row_dict in enumerate(self.report):
            if row_dict[KEY_FRAME_NUM] == n_frame:
                return index_row, row_dict
        return None, None

    def save_to_csv(self) -> bool:
        """
        Write in file the report ilst in csv format.
        :return: True if write successfully, False otherwise.

        try:
            csv_string = self.convert_to_csv()
            with open(FILE_SAVE_CSV, mode='w') as file:
                file.write(csv_string)
            return True
        except PermissionError:
            logging.error(f"Permission denied! Impossible to write the file {FILE_SAVE_CSV}!")
            return False
        """
        if len(self.report) > 0:
            now = datetime.now().strftime("%d%m%Y_%H%M%S")
            report_conv = []
            for row in self.report:
                new_row = {}
                for key, value in row.items():
                    if isinstance(key, TypeShot):
                        new_row[key.value] = row[key].value
                    else:
                        new_row[key] = row[key] + 1  # Remember: for the user the frames start at 1, for the system at 0
                report_conv.append(new_row)
            pd.DataFrame(report_conv).to_csv(FILE_SAVE_CSV.format(self.name_movie.split('.')[-2], now), index=False)
            return True
        return False

    def load_csv_from_file(self, path_csv: str) -> bool:
        """
        Read annotations from csv file.
        :param path_csv: file path of csv file.
        :return: True if read correctly, False otherwise.
        """
        with open(path_csv, 'r') as file:
            reader = csv.reader(file)
            header = next(reader)
            for row in reader:
                new_dict = {}
                for h, elem in zip(header, row):
                    if h == KEY_FRAME_NUM:
                        new_dict[h] = int(elem) - 1  # Remember: for the user the frames start at 1, for the system at 0
                    else:
                        if h == TypeShot.ANGLE.value and elem in AngleShot:
                            new_dict[TypeShot(h)] = AngleShot(elem)
                        elif h == TypeShot.LEVEL.value and elem in LevelShot:
                            new_dict[TypeShot(h)] = LevelShot(elem)
                        elif h == TypeShot.SCALE.value and elem in ScaleShot:
                            new_dict[TypeShot(h)] = ScaleShot(elem)
                        else:
                            # reset report
                            self.report = []
                            return False
                self.report.append(new_dict)
        return True

    def _add_shot_ann(self, n_frame: int, type_shot: TypeShot, annotation: JoinTypeShots) -> bool:
        """
        Method that add new row in report. The row is formatted as:
            {KEY_FRAME_NUM: n_frame, [type_shot: annotation](0-3)}
        :param n_frame: number of frame in movie.
        :param type_shot: Enum TypeShot (ANGLE; LEVEL; SCALE)
        :param annotation: Enum of AngleShot (LOW; DUTCH...), LevelShot (EYE; KNEE...)
        or ScaleShot (CLOSE; MEDIUM; LONG)
        :return: True if add new row; False otherwise.
        """
        # check correspondence between type and annotation
        if self._check_type_name_shot(type_shot, annotation):
            # Search if n_frame is in list, and find index
            index_report_search, _ = self.get_row(n_frame)

            # If index exist, modify dictionary in index-position
            if index_report_search is not None:
                self._modify_shot_ann_indexes(index_report_search, type_shot, annotation)

            # Else make new dictionary, append in list and sort
            else:
                new_row = {
                    KEY_FRAME_NUM: n_frame,
                    type_shot: annotation
                }
                # Da Python 3.10
                # bisect_right(self.report, new_row, key = lambda d: d['frame'])
                self.report.append(new_row)
                # Keep sorted the list
                self.report = sorted(self.report, key=lambda d: d[KEY_FRAME_NUM])
            return True
        return False

    def _modify_shot_ann_indexes(self, index_row: int, type_shot: TypeShot,
                                 annotation: Optional[JoinTypeShots]) -> bool:
        """
        Method that modify the row in report[index_row]. If None and the key exist, remove the key. If the row is void,
        then it's removed.
        :param index_row: Index in report.
        :param type_shot: Enum TypeShot (ANGLE; LEVEL; SCALE)
        :param annotation: Enum of AngleShot (LOW; DUTCH...), LevelShot (EYE; KNEE...)
        or ScaleShot (CLOSE; MEDIUM; LONG) or None
        :return: True if modify row[index_row]; False otherwise.
        """
        try:
            row = self.report[index_row]
            if annotation:
                row[type_shot] = annotation
            else:
                row.pop(type_shot)
                if KEY_FRAME_NUM in row and len(row) == 1:
                    self.report.pop(index_row)
            return True
        except IndexError or KeyError as e:
            logging.error(e)
            logging.error(f"Impossible modify the {index_row}-th row!")
            return False

    @staticmethod
    def _check_type_name_shot(type_shot: TypeShot, name_shot: JoinTypeShots) -> bool:
        """
        Method that check if the correspondence between TypeShot and AngelShot, LevelShot or ScaleShot is correct
        :param type_shot: Enum TypeShot (ANGLE; LEVEL; SCALE)
        :param name_shot: Enum of AngleShot (LOW; DUTCH...), LevelShot (EYE; KNEE...) or ScaleShot (CLOSE; MEDIUM; LONG)
        :return: True if the correspondence between TypeShot and AngelShot, LevelShot or ScaleShot is correct, False
        otherwise
        """
        if type_shot is TypeShot.ANGLE and isinstance(name_shot, AngleShot):
            return True
        if type_shot is TypeShot.LEVEL and isinstance(name_shot, LevelShot):
            return True
        if type_shot is TypeShot.SCALE and isinstance(name_shot, ScaleShot):
            return True
        return False

    def add_shot_ann(self, n_frame: int, type_shot: TypeShot, annotation: JoinTypeShots) -> bool:
        """
        Add new row in report
        :param n_frame: number frame
        :param type_shot: Object TypeShot
        :param annotation: AngleShot, LevelShot or ScaleShot
        :return: True if add new row; False otherwise.
        """
        return self._add_shot_ann(n_frame, type_shot, annotation)

    def modify_shot_ann_indexes(self, index_row: int, type_shot: TypeShot, annotation: Optional[JoinTypeShots]) -> bool:
        """
        Method that modify the row in report[index_row]. If None and the key exist, remove the key. If the row is void,
        then it's removed.
        :param index_row: Index in report.
        :param type_shot: Enum TypeShot (ANGLE; LEVEL; SCALE)
        :param annotation: Enum of AngleShot (LOW; DUTCH...), LevelShot (EYE; KNEE...)
        or ScaleShot (CLOSE; MEDIUM; LONG) or None
        :return: True if modify row[index_row]; False otherwise.
        """
        return self._modify_shot_ann_indexes(index_row, type_shot, annotation)
