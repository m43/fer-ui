# -*- coding: utf-8 -*-
import sys

from configuration import Configuration
from dataset import Dataset
from model.model_factory import ModelFactory

if __name__ == '__main__':
    if (len(sys.argv)) != 4:
        raise Exception("Invalid number of arguments. Got {} arguments, expected 4.".format(len(sys.argv)))

    train_path = sys.argv[1]
    test_path = sys.argv[2]
    config_path = sys.argv[3]

    config = Configuration.from_path(config_path)
    train = Dataset.from_path(train_path)
    test = Dataset.from_path(test_path)

    model = ModelFactory.get(config.model)(config)
    model.fit(train)
    model.prediction(test)
