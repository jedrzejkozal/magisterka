from ModelIfc import *
from CartesianProduct import *
from Logger import *

class HyperparamsSearch(object):

    def __init__(self):
        self.logger = Logger()


    def search_hyperparms(self, model, hyperparams_to_check):
        self.__check_model_type(model)

        all_hyperparams = self.__convert_dict_to_tuple(hyperparams_to_check)
        hyperparams_cartesian_prod = cartesian_product(all_hyperparams)
        result = self.__evaluate_all_hyperparms(model,
                                hyperparams_cartesian_prod,
                                hyperparams_to_check.keys())
        self.logger.save_logs(result, hyperparams_to_check.keys())


    def __check_model_type(self, model):
        if type(model.__class__.__bases__[0]) is not type(ModelIfc):
            raise TypeError("invalid model type")


    def __convert_dict_to_tuple(self, dict):
        result = []
        for _, item in dict.items():
            result.append(item)
        return tuple(result)


    def __evaluate_all_hyperparms(self, model, all_possible, keys):
        result = []
        for hyperparams_list in all_possible:
            evaluate_results = self.__train_and_evaluate(model,
                    self.__convert_hyperparams_to_dict(hyperparams_list, keys))
            result.append((evaluate_results, hyperparams_list))
        return result


    def __convert_hyperparams_to_dict(self, hyperparams, keys):
        result = {}
        for key, hyperparam in zip(keys, hyperparams):
            result[key] = hyperparam
        return result


    def __train_and_evaluate(self, model, hyperparams_list):
        model.train(hyperparams_list)
        return model.evaluate(hyperparams_list)
