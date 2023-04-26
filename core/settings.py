import configparser


class AutoSaveConfigParser(configparser.ConfigParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._filename = None

    def read(self, filenames, encoding=...):
        self._filename = filenames
        super().read(filenames)

    def set(self, section, option, value=None):
        super().set(section, option, str(value))
        self.save()

    def set_if_none(self, section, option, value=None):
        if self.has_option(section, option):
            return
        super().set(section, option, str(value))
        self.save()

    def add_section(self, section):
        super().add_section(section)
        self.save()

    def remove_section(self, section):
        super().remove_section(section)
        self.save()

    def remove_option(self, section, option):
        super().remove_option(section, option)
        self.save()

    def save(self):
        with open(self._filename, 'w') as file:
            self.write(file)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.save()


config = AutoSaveConfigParser()
config.read("config.ini")
