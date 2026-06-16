from __future__ import annotations

import threading
from typing import Any
from uuid import uuid4

from app.servico_analise import executar_analise_completa

_lock = threading.Lock()
_tarefas: dict[str, dict[str, Any]] = {}


def criar_tarefa() -> str:
    job_id = str(uuid4())
    with _lock:
        _tarefas[job_id] = {"status": "processing"}
    return job_id


def obter_tarefa(job_id: str) -> dict[str, Any] | None:
    with _lock:
        tarefa = _tarefas.get(job_id)
        return dict(tarefa) if tarefa else None


def _atualizar_tarefa(job_id: str, **dados: Any) -> None:
    with _lock:
        if job_id in _tarefas:
            _tarefas[job_id].update(dados)


def executar_tarefa_analise(job_id: str, parametros: dict[str, Any]) -> None:
    try:
        resultado = executar_analise_completa(**parametros)
        _atualizar_tarefa(job_id, status="completed", resultado=resultado)
    except Exception as erro:
        _atualizar_tarefa(job_id, status="failed", erro=str(erro))
