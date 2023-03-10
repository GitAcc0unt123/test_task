import yaml


class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args,
                                                                     **kwargs)
        return cls._instances[cls]


class Config(metaclass=MetaSingleton):
    flask: dict = None

    def __init__(self, path_yaml: str = 'config.yaml'):
        with open(path_yaml, 'r') as file:
            config = yaml.safe_load(file)
            self.flask = config['flask']
