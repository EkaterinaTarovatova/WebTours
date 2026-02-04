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
                        "duration": 1200, "users": 10, "spawn_rate": 1
                    },
                    {
                        "duration": 1800, "users": 15, "spawn_rate": 1
                    },
                    {
                        "duration": 2400, "users": 20, "spawn_rate": 1
                    },
                    {
                        "duration": 3000, "users": 25, "spawn_rate": 1
                    }
                ]

    def tick(self):  # стандартная функция локаста, взятая из документации, для работы с кастомными "Лоад-Шейпами"
        run_time = self.get_run_time()
        logger.debug(f"Tick called, run_time: {run_time}")

        # Считаем общее время выполнения всех стадий
        total_duration = sum(stage["duration"] for stage in self.stages)

        if run_time >= total_duration:
            logger.debug("Total duration exceeded, stopping test")
            return None

        # Находим текущую стадию
        elapsed_time = 0
        for stage in self.stages:
            if run_time < elapsed_time + stage["duration"]:
                tick_data = (stage["users"], stage["spawn_rate"])
                logger.debug(f"Returning tick data: {tick_data} for stage with duration {stage['duration']}")
                return tick_data
            elapsed_time += stage["duration"]

        return None
