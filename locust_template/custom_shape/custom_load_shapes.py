from locust import LoadTestShape
from config.config import cfg, logger


class CustomLoadShape(LoadTestShape):
    """
        Здесь должны быть описаны типы нагрузки с помощью stages
    """

    def __init__(self):
        super().__init__()
        match cfg.loadshape_type:
            case "baseline":
                self.stages = [
                    {
                        "duration": 120, "users": 10, "spawn_rate": 1
                    }
                ]
            case "stages":
                self.stages = [
                    {
                        "duration": 600, "users": 5, "spawn_rate": 1
                    },
                    {
                        "duration": 600, "users": 3, "spawn_rate": 1
                    },
                    {
                        "duration": 600, "users": 5, "spawn_rate": 1
                    },
                    {
                        "duration": 600, "users": 4, "spawn_rate": 1
                    },
                    {
                        "duration": 600, "users": 5, "spawn_rate": 1
                    }
                ]

    def tick(self):  # стандартная функция локаста, взятая из документации, для работы с кастомными "Лоад-Шейпами"
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data

        return None
