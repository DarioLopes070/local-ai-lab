from pathlib import Path

DIRETORIOS_IGNORADOS = {
    ".git",
    ".venv",
    ".vscode",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "data",
    "venv",
    ".idea",
}


ARQUIVOS_IGNORADOS = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    ".npmrc",
    ".pypirc",
}


def listar_arquivos(diretorio_base, max_arquivos=100, raiz_autorizada=None):
    """Lista arquivos sem acessar locais fora do projeto autorizado."""

    if (
        isinstance(max_arquivos, bool)
        or not isinstance(max_arquivos, int)
        or max_arquivos < 1
    ):
        raise ValueError("max_arquivos deve ser um inteiro positivo.")

    if raiz_autorizada is None:
        raise ValueError("É necessário informar uma raiz autorizada.")

    raiz = Path(raiz_autorizada).resolve(strict=True)

    if not raiz.is_dir():
        raise NotADirectoryError(f"A raiz autorizada não é um diretório: {raiz}")

    base = Path(diretorio_base).resolve(strict=True)

    if not base.is_relative_to(raiz):
        raise PermissionError("O diretório solicitado está fora da raiz autorizada.")

    if not base.is_dir():
        raise NotADirectoryError(f"O caminho informado não é um diretório: {base}")

    arquivos = []
    pendentes = [base]

    while pendentes:
        diretorio = pendentes.pop()

        for caminho in diretorio.iterdir():

            # Bloqueia links simbólicos e junctions do Windows
            if caminho.is_symlink() or caminho.is_junction():
                continue

            # Confirma que o caminho real permanece dentro da raiz
            caminho_real = caminho.resolve(strict=True)

            if not caminho_real.is_relative_to(base):
                continue

            if caminho.is_dir():

                if caminho.name in DIRETORIOS_IGNORADOS:
                    continue

                pendentes.append(caminho)

            elif caminho.is_file():

                if caminho.name in ARQUIVOS_IGNORADOS:
                    continue

                relativo = caminho.relative_to(base)
                arquivos.append(relativo.as_posix())

                if len(arquivos) >= max_arquivos:
                    return sorted(arquivos)

    return sorted(arquivos)
