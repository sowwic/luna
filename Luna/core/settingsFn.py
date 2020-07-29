import os
from Luna.utils import fileFn
from Luna.static import Directories


# class Settings:

#     DEFAULTS = {"logging":
#                 {
#                     "logLimit": 15
#                 }
#                 }

#     def __init__(self):
#         self.directory = os.path.join(os.getenv("LOCALAPPDATA"), "RigFactory")
#         self.fileName = "settings.json"
#         self.filePath = os.path.join(self.directory, self.fileName)
#         # Create default settings if missing
#         self._createMissingSettings()
#         # Load current
#         self.load()

#     def save(self, defaults: bool = False):
#         if defaults:
#             return fileFn.writeJson(self.filePath, data=self.DEFAULTS)
#         else:
#             return fileFn.writeJson(self.filePath, data=self.current)

#     def load(self) -> None:
#         self._createMissingSettings()
#         self.current = fileFn.loadJson(self.filePath)

#     def _createMissingSettings(self):
#         # Directory
#         fileFn.createMissingDir(self.directory)
#         # Default settings file
#         if not os.path.isfile(self.filePath):
#             self.save(defaults=True)


# if __name__ == "__main__":
#     testSettings = Settings()
