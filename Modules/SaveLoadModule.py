import csv
import cv2
import os
import pickle
import pandas as pd
from typing import List

from Models.Enums.GameMode import GAME_MODE
from Models.SavedData.SavedRow import SavedRow
from Models.Settings.Settings import Settings
from Models.SettingsTransitionData import SettingsTransitionData
from Utilities.Constants import *
from Utilities.OpenFile import open_file

class SaveLoadModule:
    csv_column_names = [PATH_ID, PATH_NAME, PATH_GAME_MODE, POINT_X, POINT_Y, POINT_IS_GOOD, POINT_ORDER, POINT_ALPHABET]
    
    def __init__(self):
        self.settings = Settings()
        self.locale = 'ch'
        self.saved_rows: List[SavedRow] = []


    def load_settings(self) -> Settings:
        try:
            with open( open_file(f"{SETTINGS_FILE_LOCATION}Settings.pkl"), 'rb') as file:
                variables = pickle.load(file)
                self.settings.convert_from(variables)
        except:
            self.save_settings(self.settings)
        return self.settings


    def save_settings(self, settings):
        variables = settings.convert_to_variables()
        with open( open_file(f"{SETTINGS_FILE_LOCATION}Settings.pkl"), 'wb') as file:
            pickle.dump(variables, file)
        self.settings = settings


    def load_locale(self):
        try:
            with open( open_file(f"{SETTINGS_FILE_LOCATION}LocaleSettings.pkl"), 'rb') as file:
                variables = pickle.load(file)
                self.locale = variables[LOCALE]
        except:
            self.save_locale(self.locale)
        return self.locale


    def save_locale(self, locale):
        variables = {
            LOCALE: locale
        }
        with open( open_file(f"{SETTINGS_FILE_LOCATION}LocaleSettings.pkl"), 'wb') as file:
            pickle.dump(variables, file)
        self.locale = locale


    def load_path_data(self) -> List[SavedRow]:
        try:
            df = pd.read_csv( open_file(PATH_FILE_LOCATION), usecols=self.csv_column_names, keep_default_na=False).sort_values(by=['path_id'])
            df_dict = df.to_dict()
            df_list = df.values.tolist()
            savedRows: List[SavedRow] = []
            for i in range(len(df_list)):
                savedData = SavedRow(
                    path_id=df_dict[PATH_ID][i], 
                    path_name=df_dict[PATH_NAME][i], 
                    path_game_mode=GAME_MODE(df_dict[PATH_GAME_MODE][i]), 
                    point_x=float(df_dict[POINT_X][i]),
                    point_y=float(df_dict[POINT_Y][i]),
                    point_is_good=df_dict[POINT_IS_GOOD][i],
                    point_order=int(df_dict[POINT_ORDER][i]),
                    point_alphabet=df_dict[POINT_ALPHABET][i]
                )
                savedRows.append(savedData)
            self.saved_rows = savedRows
        except:
            settings_transition_data = SettingsTransitionData(settings=self.settings, saved_rows=self.saved_rows, renamed_paths=[], updated_path_images=[])
            self.save_path_data(settings_transition_data=settings_transition_data)
        return self.saved_rows


    def save_path_data(self, settings_transition_data: SettingsTransitionData):
        # Save path data
        if len(settings_transition_data.saved_rows) > 0:
            saved_path_data = []
            for row in settings_transition_data.saved_rows:
                saved_row = [row.path_id, row.path_name, row.path_game_mode.value, row.point_x, row.point_y, row.point_is_good, row.point_order, row.point_alphabet]
                saved_path_data.append(saved_row)
            df = pd.DataFrame(saved_path_data, columns=self.csv_column_names)
            df.to_csv( open_file(PATH_FILE_LOCATION) )
        else:
            df = pd.DataFrame([['','','','','','','','']], columns=self.csv_column_names)
            df = df[df.path_id != '']
            df.to_csv( open_file(PATH_FILE_LOCATION) )

        # Save path images
        for path_image in settings_transition_data.updated_path_images:
            cv2.imwrite(open_file(f"{PATH_IMAGE_FILE_LOCATION}{CURRENT_PATH_SET}_{path_image.path_id}.jpg"), path_image.image)
        
        # Delete old files
        old_path_ids = []
        for row in self.saved_rows:
            old_path_ids.append(row.path_id)
        old_path_ids = list(set(old_path_ids))
        
        new_path_ids = []
        for row in settings_transition_data.saved_rows:
            new_path_ids.append(row.path_id)
        new_path_ids = list(set(new_path_ids))

        deleted_path_ids = list(set(old_path_ids) - set(new_path_ids))

        for row in deleted_path_ids:
            old_file_name = open_file(f"{PATH_IMAGE_FILE_LOCATION}{CURRENT_PATH_SET}_{row}.jpg")
            if os.path.exists(old_file_name):
                os.remove(old_file_name)

        # Rename files
        for rename_path in settings_transition_data.renamed_paths:
            old_file_name = open_file(f"{PATH_IMAGE_FILE_LOCATION}{CURRENT_PATH_SET}_{rename_path.old_name}.jpg")
            new_file_name = open_file(f"{PATH_IMAGE_FILE_LOCATION}{CURRENT_PATH_SET}_{rename_path.new_name}.jpg")
            if os.path.exists(old_file_name):
                os.rename(old_file_name, new_file_name)

        self.saved_rows = settings_transition_data.saved_rows