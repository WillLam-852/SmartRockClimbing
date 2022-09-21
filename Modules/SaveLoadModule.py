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
    csv_column_names = [PATH_ID, PATH_NAME, PATH_GAMEMODE, POINT_X, POINT_Y, POINT_IS_GOOD, POINT_ORDER, POINT_ALPHABET]
    
    def __init__(self):
        self.settings = Settings()
        self.locale = 'ch'
        self.path_data: List[SavedRow] = []


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
            savedRows: List[SavedRow] = []
            for row in df.values.tolist():
                savedData = SavedRow(
                    path_id=row[PATH_ID], 
                    path_name=row[PATH_NAME], 
                    path_game_mode=GAME_MODE(row[PATH_GAMEMODE]), 
                    point_x=int(row[POINT_X]),
                    point_y=int(row[POINT_Y]),
                    point_is_good=row[POINT_IS_GOOD],
                    point_order=int(row[POINT_ORDER]),
                    point_alphabet=row[POINT_ALPHABET]
                )
                savedRows.append(savedData)
            self.path_data = savedRows
        except:
            self.save_path_data(self.path_data)
        return self.path_data


    def save_path_data(self, settings_transition_data: SettingsTransitionData):
        # Save path data
        if len(settings_transition_data.saved_rows) > 0:
            for row in settings_transition_data.saved_rows:
                saved_row = [row.path_id, row.path_name, row.path_game_mode.value, row.point_x, row.point_y, row.point_is_good, row.point_order, row.point_alphabet]
                df = pd.DataFrame([saved_row], columns=self.csv_column_names)
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
        for row in self.path_data:
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

        self.path_data = settings_transition_data.saved_rows