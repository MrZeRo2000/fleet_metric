
class PredictorService:
    def set_up(self):
        pass

    def get_predict_params(self, category_id=None):
        raise NotImplementedError("Method get_predict_params not implemented")

    def calc_test(self, df, predict_params):
        raise NotImplementedError("Method predict_test not implemented")

    def calc_predict(self, df, predict_params):
        raise NotImplementedError("Method predict_test not implemented")

    def get_data_result(self):
        raise NotImplementedError("Method predict_test not implemented")

