from __future__ import annotations
from Models.Path.PathImage import PathImage
from Models.Path.RenamedPath import RenamedPath
from Models.SavedData.SavedRow import SavedRow
from Models.Settings.Settings import Settings

class SettingsTransitionData:
    """
    A class that used to transfer data between SettingsScreen, PathsScreen & CameraScreen in Settings

    Attributes
    ----------
    settings : Settings
    saved_rows : list[SavedRow]
    renamed_paths : list[RenamedPath]
    updated_path_images : list[PathImage]
    """

    def __init__(self, settings:Settings, saved_rows:list[SavedRow], renamed_paths:list[RenamedPath], updated_path_images:list[PathImage]):
        self.settings = settings
        self.saved_rows = saved_rows
        self.renamed_paths = renamed_paths
        self.updated_path_images = updated_path_images