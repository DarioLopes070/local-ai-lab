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

EXTENSOES_PERMITIDAS = {".py", ".md", ".json", ".txt"}

MAX_TAMANHO_ARQUIVO = 100_000  # 100 KB, aproximadamente


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


def ler_arquivo(caminho_arquivo, raiz_autorizada):
    """Lê um arquivo de texto dentro da raiz autorizada."""

    raiz = Path(raiz_autorizada).resolve(strict=True)

    if not raiz.is_dir():
        raise NotADirectoryError(f"A raiz autorizada não é um diretório: {raiz}")

    caminho = Path(caminho_arquivo)

    # Caminhos relativos são interpretados dentro do projeto
    if not caminho.is_absolute():
        caminho = raiz / caminho

    # Bloqueia links simbólicos e junctions no caminho completo
    for parte in [caminho, *caminho.parents]:
        if parte == raiz:
            break

        if parte.is_symlink() or parte.is_junction():
            raise PermissionError(
                "Acesso por link simbólico ou junction não permitido."
            )

    arquivo = caminho.resolve(strict=True)

    if not arquivo.is_relative_to(raiz):
        raise PermissionError("O arquivo solicitado está fora da raiz autorizada.")

    relativo = arquivo.relative_to(raiz)

    if any(parte in DIRETORIOS_IGNORADOS for parte in relativo.parts[:-1]):
        raise PermissionError("O diretório não permite leitura.")

    if arquivo.name in ARQUIVOS_IGNORADOS:
        raise PermissionError("Arquivo sensível não permitido.")

    if arquivo.suffix.lower() not in EXTENSOES_PERMITIDAS:
        raise ValueError(f"Extensão não permitida: {arquivo.suffix}")

    if not arquivo.is_file():
        raise IsADirectoryError(f"O caminho não corresponde a um arquivo: {arquivo}")

    if arquivo.stat().st_size > MAX_TAMANHO_ARQUIVO:
        raise ValueError("O arquivo excede o limite de tamanho permitido.")

    return arquivo.read_text(encoding="utf-8")
