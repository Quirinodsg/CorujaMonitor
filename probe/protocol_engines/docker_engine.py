"""
Docker Engine - Coleta métricas de containers via Docker SDK
Retorna status=unknown com error="engine_unavailable" se docker não instalado.
"""
import logging
from typing import Optional

from .base_engine import BaseProtocolEngine, EngineResult

logger = logging.getLogger(__name__)

try:
    import docker
    _DOCKER_AVAILABLE = True
except ImportError:
    _DOCKER_AVAILABLE = False


class DockerEngine(BaseProtocolEngine):
    """
    Engine para coleta de métricas de containers Docker.

    kwargs esperados em execute():
        container_name (str): nome ou ID do container (None = todos)
        base_url (str): URL do daemon Docker (padrão: unix:///var/run/docker.sock)
        collect_stats (bool): coletar CPU/memória via stats API (padrão: True)
    """

    def is_available(self) -> bool:
        if not _DOCKER_AVAILABLE:
            return False
        try:
            client = docker.from_env()
            client.ping()
            return True
        except Exception:
            return False

    def execute(self, host: str, **kwargs) -> EngineResult:
        if not _DOCKER_AVAILABLE:
            return self._unavailable_result()

        container_name: Optional[str] = kwargs.get("container_name")
        base_url: Optional[str] = kwargs.get("base_url")
        collect_stats: bool = kwargs.get("collect_stats", True)

        try:
            if base_url:
                client = docker.DockerClient(base_url=base_url)
            else:
                client = docker.from_env()

            client.ping()

            if container_name:
                containers = [client.containers.get(container_name)]
            else:
                containers = client.containers.list(all=True)

            container_data = []
            running_count = 0

            for c in containers:
                info = {
                    "id": c.short_id,
                    "name": c.name,
                    "status": c.status,
                    "image": c.image.tags[0] if c.image.tags else c.image.short_id,
                }

                if collect_stats and c.status == "running":
                    running_count += 1
                    try:
                        stats = c.stats(stream=False)
                        info["cpu_percent"] = self._calc_cpu_percent(stats)
                        info["memory_mb"] = round(
                            stats.get("memory_stats", {}).get("usage", 0) / 1024 / 1024, 2
                        )
                        info["memory_limit_mb"] = round(
                            stats.get("memory_stats", {}).get("limit", 0) / 1024 / 1024, 2
                        )
                    except Exception as e:
                        logger.debug(f"DockerEngine stats error for {c.name}: {e}")
                elif c.status == "running":
                    running_count += 1

                container_data.append(info)

            total = len(container_data)
            status = "ok" if running_count > 0 or total == 0 else "warning"

            return EngineResult(
                status=status,
                value=float(running_count),
                unit="containers",
                metadata={
                    "host": host,
                    "total_containers": total,
                    "running_containers": running_count,
                    "containers": container_data,
                },
            )

        except docker.errors.DockerException as e:
            logger.warning(f"DockerEngine connection error for {host}: {e}")
            return EngineResult(
                status="unknown",
                error="docker_unavailable",
                metadata={"host": host, "detail": str(e)},
            )
        except Exception as e:
            logger.error(f"DockerEngine error for {host}: {e}")
            return EngineResult(
                status="unknown",
                error=str(e),
                metadata={"host": host},
            )

    def _calc_cpu_percent(self, stats: dict) -> float:
        """Calcula % CPU a partir das stats do Docker"""
        try:
            cpu_delta = (
                stats["cpu_stats"]["cpu_usage"]["total_usage"]
                - stats["precpu_stats"]["cpu_usage"]["total_usage"]
            )
            system_delta = (
                stats["cpu_stats"]["system_cpu_usage"]
                - stats["precpu_stats"]["system_cpu_usage"]
            )
            num_cpus = stats["cpu_stats"].get("online_cpus") or len(
                stats["cpu_stats"]["cpu_usage"].get("percpu_usage", [1])
            )
            if system_delta > 0 and cpu_delta >= 0:
                return round((cpu_delta / system_delta) * num_cpus * 100.0, 2)
        except (KeyError, ZeroDivisionError):
            pass
        return 0.0
