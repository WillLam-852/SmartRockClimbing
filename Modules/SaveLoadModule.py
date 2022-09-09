import pickle
# import os
from typing import List
# import cv2
import pandas as pd
from Models.SavedData import SavedData
from Models.Settings import Settings
from Models.Enums.GameMode import GAME_MODE
from Utilities.Constants import *
from Utilities.OpenFile import open_file

class SaveLoadModule:
    csv_column_names = [PATH_ID, PATH_NAME, PATH_GAMEMODE, POINT_X, POINT_Y, POINT_IS_GOOD, POINT_ORDER, POINT_ALPHABET]
    
    def __init__(self):
        self.settings = Settings()
        self.locale = 'ch'
        self.path_data: List[SavedData] = []
        self.path_images = []


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


    def load_path_data(self) -> List[SavedData]:
        try:
            df = pd.read_csv( open_file(PATH_FILE_LOCATION), usecols=self.csv_column_names, keep_default_na=False).sort_values(by=['path_id'])
            savedFile: List[SavedData] = []
            for row in df.values.tolist():
                savedData = SavedData(
                    path_id=row[PATH_ID], 
                    path_name=row[PATH_NAME], 
                    path_gamemode=GAME_MODE(row[PATH_GAMEMODE]), 
                    point_x=int(row[POINT_X]),
                    point_y=int(row[POINT_Y]),
                    point_is_good=row[POINT_IS_GOOD],
                    point_order=int(row[POINT_ORDER]),
                    point_alphabet=row[POINT_ALPHABET]
                )
                savedFile.append(savedData)
            self.path_data = savedFile
        except:
            self.save_path_data(self.path_data)
        return self.path_data


    # def save_path_data(self, path_data, rename_paths=[], path_images=[]):
    #     if len(path_data) > 0:
    #         df = pd.DataFrame(path_data, columns=self.csv_column_names)
    #         df.to_csv( open_file(PATH_FILE_LOCATION) )
    #     else:
    #         df = pd.DataFrame([['','','','','','','','']], columns=self.csv_column_names)
    #         df = df[df.path_id != '']
    #         df.to_csv( open_file(PATH_FILE_LOCATION) )

    #     # Save path images
    #     for image in path_images:
    #         cv2.imwrite(open_file(f"{PATH_IMAGE_FILE_LOCATION}{CURRENT_PATH_SET}_{image[0]}.jpg"), image[1])
        
    #     # Delete old files
    #     old_path_ids = []
    #     for row in self.path_data:
    #         old_path_ids.append(row[0])
    #     old_path_ids = list(set(old_path_ids))
        
    #     new_path_ids = []
    #     for row in path_data:
    #         new_path_ids.append(row[0])
    #     new_path_ids = list(set(new_path_ids))

    #     deleted_path_ids = list(set(old_path_ids) - set(new_path_ids))

    #     for row in deleted_path_ids:
    #         old_file_name = open_file(f"{PATH_IMAGE_FILE_LOCATION}{CURRENT_PATH_SET}_{row}.jpg")
    #         if os.path.exists(old_file_name):
    #             os.remove(old_file_name)

    #     # Rename files
    #     for rename_path in rename_paths:
    #         old_file_name = open_file(f"{PATH_IMAGE_FILE_LOCATION}{CURRENT_PATH_SET}_{rename_path[0]}.jpg")
    #         new_file_name = open_file(f"{PATH_IMAGE_FILE_LOCATION}{CURRENT_PATH_SET}_{rename_path[1]}.jpg")
    #         if os.path.exists(old_file_name):
    #             os.rename(old_file_name, new_file_name)

    #     self.path_data = path_data