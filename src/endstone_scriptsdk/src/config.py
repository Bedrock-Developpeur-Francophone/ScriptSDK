import json, os, typing

if typing.TYPE_CHECKING:
    from endstone_scriptsdk.scriptsdk import ScriptSDK

class Config:

    _folder = 'plugins/ScriptSDK'
    _file = 'plugins/ScriptSDK/config.json'

    config = {}

    # Database :
    database_enable = False
    postgres_host = 'localhost'
    postgres_port = 5432
    postgres_user = 'postgres'
    postgres_password = 'postgres'
    postgres_database = 'postgres'

    def __init__(self, plugin : "ScriptSDK"):
        if not os.path.exists(self._folder):
            os.mkdir(self._folder)
        if not os.path.exists(self._file):
            self.config = self._get_default()
            self.save()
            plugin.logger.info('Config loaded and created !')
        else:
            self.load()
            plugin.logger.info('Config loaded !')

    def _get_default(self):
        return {
            'modules' : {
                'database' : self.database_enable
            },
            'database' : {
                'postgres_host': self.postgres_host,
                'postgres_port': self.postgres_port,
                'postgres_user': self.postgres_user,
                'postgres_password': self.postgres_password,
                'postgres_database': self.postgres_database
            }
        }
    
    def _valid_config(self, config, default = None):
        if default is None:
            default = self._get_default()
        
        for key, value in default.items():
            if not key in config:  
                return False
            if isinstance(value, dict):
                if not self._valid_config(config[key], value):
                    return False
        return True

    def load(self):
        with open(self._file, 'r') as file:
            self.config = json.load(file)
            
            if not self._valid_config(self.config):
                raise Exception('Your configuration file is invalid! Please delete it and reload the server. (plugins/ScriptSDK/config.json)')
            
            # Modules
            self.database_enable = self.config['modules']['database']

            # Database
            self.postgres_host = self.config['database']['postgres_host']
            self.postgres_port = self.config['database']['postgres_port']
            self.postgres_user = self.config['database']['postgres_user']
            self.postgres_password = self.config['database']['postgres_password']
            self.postgres_database = self.config['database']['postgres_database']

    def save(self):
        with open(self._file, 'w+') as file:
            json.dump(self.config, file, indent=5)