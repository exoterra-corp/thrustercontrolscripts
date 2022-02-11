import configparser
from configparser import ConfigParser
from os.path import exists
from traceback import extract_tb

class ConfigManager:
    """
    This class has 2 objectives 1st is to locate the eds file if there is one locally
    and the other is to load config data from an config(ini) file
    """
    def __init__(self, config_file = None):
        try:
            self.config_file = config_file
            self.parser = ConfigParser()
            if self.config_file == None:
                #look for default file
                self.config_file = "./conf/default.conf"
                if exists(self.config_file):
                    print(f"Found {self.config_file}!")
                    with open(self.config_file) as e:
                        self.parser.read_file(e)
                        self.parser.get()

        except Exception as e:
            print(extract_tb(None))
            print(e)

    def get_parser(self):
        return self.parser

    def get(self, section, key, type=str):
        """
        wrapper function for get that handles invalid sections, keys
        """
        val = None
        try:
            if type == str:
                val = self.parser[section][key]
            elif type == int:
                val = self.parser.getint(section,key)
            elif type == bool:
                val = self.parser.getboolean(section,key)
        except configparser.NoOptionError:
            None
        finally:
            return val