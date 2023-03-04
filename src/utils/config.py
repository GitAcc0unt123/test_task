import yaml


class Config():
    """Конфигурации сервисов.

    Attributes:
        flask: Конфигурация Flask приложения.
    """
    flask: dict

    def __init__(self, path_yaml: str = 'config.yaml') -> None:
        """Инициализирует экземпляр класса.

        Args:
            path_yaml: Путь к конфигурационному файлу в формате yaml.
        """
        with open(path_yaml, 'r') as file:
            config = yaml.safe_load(file)
            self.flask = config['flask']
