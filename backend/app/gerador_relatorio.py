from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import markdown


def salvar_relatorio(
    *,
    diretorio_relatorios: str,
    nome_teste: str,
    relatorio_markdown: str,
) -> tuple[Path, Path]:
    nome_seguro = re.sub(r"[^\w\-]+", "_", nome_teste.lower()).strip("_") or "teste"
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = Path(diretorio_relatorios) / f"{nome_seguro}_{carimbo}"
    base.parent.mkdir(parents=True, exist_ok=True)

    caminho_md = base.with_suffix(".md")
    caminho_html = base.with_suffix(".html")

    caminho_md.write_text(relatorio_markdown, encoding="utf-8")

    corpo_html = markdown.markdown(relatorio_markdown, extensions=["tables", "fenced_code"])
    caminho_html.write_text(
        f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <title>{nome_teste} — Relatório A/B Méliuz</title>
  <style>
    body {{ font-family: Inter, Segoe UI, sans-serif; max-width: 920px; margin: 40px auto; padding: 0 24px; color: #1a1a2e; line-height: 1.6; }}
    h1,h2,h3 {{ color: #e85d04; }}
    table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
    th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
    th {{ background: #fff5eb; }}
    code {{ background: #f4f4f8; padding: 2px 6px; border-radius: 4px; }}
  </style>
</head>
<body>{corpo_html}</body>
</html>""",
        encoding="utf-8",
    )

    return caminho_md, caminho_html


def montar_resumo_resultado(relatorio_markdown: str, decisao: str) -> str:
    linhas = [linha.strip("- ").strip() for linha in relatorio_markdown.splitlines() if linha.strip().startswith("-")]
    if linhas:
        resumo = " | ".join(linhas[:3])
        return re.sub(r"\*\*(.+?)\*\*", r"\1", resumo)
    return re.sub(r"\*\*(.+?)\*\*", r"\1", decisao)[:280]
