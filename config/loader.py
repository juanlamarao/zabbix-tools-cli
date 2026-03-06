import yaml
import os


class ConfigLoader:

    def __init__(self, profile):
        self.profile = profile
        self.config = self.load()

    def load(self):

        path = f"config/profiles/{self.profile}.yaml"

        if not os.path.exists(path):
            raise Exception(f"Profile {self.profile} not found")

        with open(path) as f:
            return yaml.safe_load(f)

    def get(self):
        return self.config