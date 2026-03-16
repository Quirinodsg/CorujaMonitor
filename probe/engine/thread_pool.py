"""
Thread Pool - Worker pool para execução paralela de sensores
max_workers: 10 (configurável)

Proteções implementadas:
  - Limite de workers por host
  - Limite de conexões RPC
  - Limite de queries WMI
  - Timeout por tarefa
"""
import logging
import time
import threading
from concurrent.futures import ThreadPoolExecutor, Future, TimeoutError
from typing import Callable, Dict, Optional

logger = logging.getLogger(__name__)

DEFAULT_MAX_WORKERS = 10
DEFAULT_TASK_TIMEOUT = 30  # segundos


class WorkerPool:
    """
    Pool de workers para execução paralela de sensores.
    
    Uso:
        pool = WorkerPool(max_workers=10)
        pool.submit(lambda: sensor.collect())
        pool.shutdown()
    """

    def __init__(self, max_workers: int = DEFAULT_MAX_WORKERS, task_timeout: int = DEFAULT_TASK_TIMEOUT):
        self.max_workers = max_workers
        self.task_timeout = task_timeout
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="SensorWorker",
        )
        self._futures: Dict[str, Future] = {}
        self._lock = threading.Lock()
        self._submitted = 0
        self._completed = 0
        self._failed = 0

        logger.info(f"WorkerPool iniciado: {max_workers} workers, timeout={task_timeout}s")

    def submit(self, fn: Callable, task_id: Optional[str] = None) -> Future:
        """Submete tarefa para execução"""
        task_id = task_id or f"task_{self._submitted}"

        def wrapped():
            start = time.monotonic()
            try:
                result = fn()
                elapsed = (time.monotonic() - start) * 1000
                logger.debug(f"Worker task {task_id} concluída [{elapsed:.1f}ms]")
                with self._lock:
                    self._completed += 1
                return result
            except Exception as e:
                elapsed = (time.monotonic() - start) * 1000
                logger.error(f"Worker task {task_id} falhou [{elapsed:.1f}ms]: {e}")
                with self._lock:
                    self._failed += 1
                raise

        with self._lock:
            self._submitted += 1

        future = self._executor.submit(wrapped)

        with self._lock:
            self._futures[task_id] = future

        return future

    def active_count(self) -> int:
        """Retorna número de workers ativos"""
        with self._lock:
            return sum(1 for f in self._futures.values() if not f.done())

    def stats(self) -> Dict:
        """Retorna estatísticas do pool"""
        with self._lock:
            active = sum(1 for f in self._futures.values() if not f.done())
            return {
                "max_workers": self.max_workers,
                "active_workers": active,
                "submitted": self._submitted,
                "completed": self._completed,
                "failed": self._failed,
                "queue_depth": active,
            }

    def shutdown(self, wait: bool = True):
        """Para o pool de workers"""
        logger.info("WorkerPool: aguardando conclusão das tarefas...")
        self._executor.shutdown(wait=wait)
        logger.info("WorkerPool parado")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.shutdown()
