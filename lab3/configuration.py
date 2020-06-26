from configparser import ConfigParser


class Configuration:
    MODE_VERBOSE = "verbose"
    MODE_TEST = "test"
    KEYWORD_MODE = "mode"
    KEYWORD_MODEL = "model"
    KEYWORD_MAX_DEPTH = "max_depth"
    KEYWORD_NUMBER_OF_TREES = "num_trees"
    KEYWORD_FEATURE_RATIO = "feature_ratio"
    KEYWORD_EXAMPLE_RATIO = "example_ratio"

    DEFAULT_MAX_DEPTH = -1  # (inf)
    DEFAULT_NUMBER_OF_TREES = 1
    DEFAULT_FEATURE_RATIO = 1
    DEFAULT_EXAMPLE_RATIO = 1

    def __init__(self, dict):
        self.mode = dict.get(self.KEYWORD_MODE)
        self.model = dict.get(self.KEYWORD_MODEL)
        self.max_depth = int(dict.get(self.KEYWORD_MAX_DEPTH, self.DEFAULT_MAX_DEPTH))
        self.num_trees = int(dict.get(self.KEYWORD_NUMBER_OF_TREES, self.DEFAULT_NUMBER_OF_TREES))
        self.feature_ratio = float(dict.get(self.KEYWORD_FEATURE_RATIO, self.DEFAULT_FEATURE_RATIO))
        self.example_ratio = float(dict.get(self.KEYWORD_EXAMPLE_RATIO, self.DEFAULT_EXAMPLE_RATIO))

    @staticmethod
    def from_path(path):
        cfg = ConfigParser()
        cfg.read_string("[CONFIG]\n" + open(path).read())
        return Configuration(dict(cfg["CONFIG"].items()))

    def is_verbose_mode(self):
        return self.mode == self.MODE_VERBOSE

    def is_test_mode(self):
        return self.mode == self.MODE_TEST
