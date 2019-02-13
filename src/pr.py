
from ps import PredictorService
from aps import ARIMAPredictionService
from context import inject, component


@component
class PredictServiceResolver:

    # noinspection PyPropertyDefinition
    @property
    @inject
    def arima_predictor_service(self) -> ARIMAPredictionService: pass

    def get_service(self, predictor_type) -> PredictorService:
        return self.arima_predictor_service
