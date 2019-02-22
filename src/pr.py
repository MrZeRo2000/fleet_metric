
from ps import PredictorService
from aps import ARIMAPredictionService
from sps import SupervisedPredictionService
from context import inject, component


@component
class PredictServiceResolver:

    # noinspection PyPropertyDefinition
    @property
    @inject
    def arima_predictor_service(self) -> ARIMAPredictionService: pass

    # noinspection PyPropertyDefinition
    @property
    @inject
    def supervised_predictor_service(self) -> SupervisedPredictionService: pass

    def get_service(self, predictor_type) -> PredictorService:
        predictor_services = {
            "ARIMA": self.arima_predictor_service,
            "SUPERVISED": self.supervised_predictor_service
        }

        return predictor_services[predictor_type]
