from model.id3 import ID3
from model.rf import RandomForrest


class ModelFactory:
    # TODO use dynamic binding to accomplish this
    @staticmethod
    def get(name):
        if name.lower() == "id3":
            return ID3
        if name.lower() == "rf":
            return RandomForrest
        else:
            raise ValueError("No")