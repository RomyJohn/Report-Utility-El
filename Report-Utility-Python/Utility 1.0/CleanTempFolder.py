import os, sys, configparser, shutil

def loadConfigProperties():
    try:
        filePath = os.path.join(sys.path[0], fr'Resources\config.properties')
        configReader = configparser.ConfigParser()
        configReader.read(filePath)
        return configReader
    except:
        print(f'Failed to load config.properties')

def cleanTempFolder(tempFolderPath):
    try:
        tempFolderPathFolders = os.listdir(tempFolderPath)
        for folders in tempFolderPathFolders:
            foldersPath = os.path.join(tempFolderPath, folders)
            shutil.rmtree(foldersPath, ignore_errors=False)
    except:
        print(f'Failed in cleaning {tempFolderPath}')

config = loadConfigProperties()

tempFolderPath = config.get('path', 'tempFolderPath')

cleanTempFolder(tempFolderPath)
