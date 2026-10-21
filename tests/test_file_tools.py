import pytest

from src.tools.file_tools import listar_arquivos, ler_arquivo


@pytest.fixture
def projeto_temporario(tmp_path):
    """Cria um projeto fictício para testar a listagem."""

    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / ".git").mkdir()
    (tmp_path / ".vscode").mkdir()
    (tmp_path / "data").mkdir()

    (tmp_path / "README.md").write_text("# Projeto de teste", encoding="utf-8")
    (tmp_path / "src" / "app.py").write_text("print('Olá')", encoding="utf-8")
    (tmp_path / "tests" / "test_app.py").write_text(
        "def test_exemplo(): pass", encoding="utf-8"
    )
    (tmp_path / ".git" / "config").write_text("configuração interna", encoding="utf-8")
    (tmp_path / ".vscode" / "settings.json").write_text("{}", encoding="utf-8")
    (tmp_path / "data" / "conversations.db").write_text(
        "dados privados", encoding="utf-8"
    )
    (tmp_path / ".env").write_text("TOKEN=segredo", encoding="utf-8")

    return tmp_path


def test_listar_arquivos_permitidos(projeto_temporario):
    arquivos = listar_arquivos(projeto_temporario, raiz_autorizada=projeto_temporario)

    assert arquivos == [
        "README.md",
        "src/app.py",
        "tests/test_app.py",
    ]


def test_listar_arquivos_ignora_diretorios_internos(projeto_temporario):
    arquivos = listar_arquivos(projeto_temporario, raiz_autorizada=projeto_temporario)

    assert ".git/config" not in arquivos
    assert ".vscode/settings.json" not in arquivos
    assert "data/conversations.db" not in arquivos


def test_listar_arquivos_ignora_arquivos_sensiveis(projeto_temporario):
    arquivos = listar_arquivos(projeto_temporario, raiz_autorizada=projeto_temporario)

    assert ".env" not in arquivos


def test_listar_arquivos_rejeita_caminho_inexistente(tmp_path):
    caminho = tmp_path / "projeto_inexistente"

    with pytest.raises(FileNotFoundError):
        listar_arquivos(caminho, raiz_autorizada=tmp_path)


def test_listar_arquivos_rejeita_arquivo_como_diretorio(tmp_path):
    arquivo = tmp_path / "arquivo.txt"
    arquivo.write_text("conteúdo", encoding="utf-8")

    with pytest.raises(NotADirectoryError):
        listar_arquivos(arquivo, raiz_autorizada=tmp_path)


def test_listar_arquivos_nao_segue_link_para_diretorio_externo(tmp_path):
    """Garante que links simbólicos não exponham arquivos externos."""

    projeto = tmp_path / "projeto"
    projeto.mkdir()

    externo = tmp_path / "privado"
    externo.mkdir()

    (externo / "segredo.txt").write_text(
        "informação confidencial",
        encoding="utf-8",
    )

    link = projeto / "atalho"

    try:
        link.symlink_to(externo, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Criação de links simbólicos não disponível neste ambiente.")

    arquivos = listar_arquivos(projeto, raiz_autorizada=projeto)

    assert arquivos == []


import os
import subprocess


@pytest.mark.skipif(os.name != "nt", reason="Teste específico do Windows")
def test_listar_arquivos_nao_segue_junction_externa(tmp_path):
    """Impede que uma junction exponha arquivos fora do projeto."""

    projeto = tmp_path / "projeto"
    projeto.mkdir()

    externo = tmp_path / "privado"
    externo.mkdir()

    (externo / "segredo.txt").write_text(
        "informação confidencial",
        encoding="utf-8",
    )

    junction = projeto / "atalho"

    resultado = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(junction), str(externo)],
        capture_output=True,
        check=False,
    )

    if resultado.returncode != 0:
        pytest.skip("Não foi possível criar uma junction neste Windows.")

    arquivos = listar_arquivos(projeto, raiz_autorizada=projeto)

    assert "atalho/segredo.txt" not in arquivos


def test_listar_arquivos_respeita_limite(tmp_path):
    """Garante que a listagem respeite o limite configurado."""

    for indice in range(10):
        (tmp_path / f"arquivo_{indice}.py").write_text(
            "print('teste')",
            encoding="utf-8",
        )

    arquivos = listar_arquivos(tmp_path, max_arquivos=3, raiz_autorizada=tmp_path)

    assert len(arquivos) == 3
    assert len(set(arquivos)) == 3


@pytest.mark.parametrize("limite", [0, -1, 1.5, "10", True])
def test_listar_arquivos_rejeita_limite_invalido(tmp_path, limite):
    """Rejeita limites que não sejam inteiros positivos."""

    with pytest.raises(ValueError):
        listar_arquivos(tmp_path, max_arquivos=limite, raiz_autorizada=tmp_path)


def test_listar_arquivos_bloqueia_diretorio_externo(tmp_path):
    """Impede listar diretórios fora da raiz autorizada."""

    autorizado = tmp_path / "autorizado"
    autorizado.mkdir()

    externo = tmp_path / "externo"
    externo.mkdir()

    (externo / "segredo.txt").write_text(
        "informação privada",
        encoding="utf-8",
    )

    with pytest.raises(PermissionError):
        listar_arquivos(
            externo,
            raiz_autorizada=autorizado,
        )


def test_listar_arquivos_exige_raiz_autorizada(tmp_path):
    """Não permite listagem sem uma raiz explicitamente definida."""

    with pytest.raises(ValueError):
        listar_arquivos(tmp_path)


def test_ler_arquivo_permitido(tmp_path):
    """Lê um arquivo permitido dentro da raiz autorizada."""

    arquivo = tmp_path / "exemplo.py"
    arquivo.write_text("print('Olá, mundo!')", encoding="utf-8")

    conteudo = ler_arquivo("exemplo.py", raiz_autorizada=tmp_path)

    assert conteudo == "print('Olá, mundo!')"


def test_ler_arquivo_bloqueia_acesso_externo(tmp_path):
    """Impede a leitura de arquivos fora da raiz autorizada."""

    projeto = tmp_path / "projeto"
    projeto.mkdir()

    externo = tmp_path / "segredo.txt"
    externo.write_text("informação privada", encoding="utf-8")

    with pytest.raises(PermissionError):
        ler_arquivo(externo, raiz_autorizada=projeto)


def test_ler_arquivo_bloqueia_env(tmp_path):
    """Impede a leitura de arquivos de configuração sensíveis."""

    arquivo = tmp_path / ".env"
    arquivo.write_text("API_KEY=segredo", encoding="utf-8")

    with pytest.raises(PermissionError):
        ler_arquivo(".env", raiz_autorizada=tmp_path)


def test_ler_arquivo_bloqueia_extensao_invalida(tmp_path):
    """Rejeita arquivos com extensões não autorizadas."""

    arquivo = tmp_path / "programa.exe"
    arquivo.write_bytes(b"conteudo de teste")

    with pytest.raises(ValueError):
        ler_arquivo("programa.exe", raiz_autorizada=tmp_path)


def test_ler_arquivo_bloqueia_arquivo_grande(tmp_path):
    """Impede a leitura de arquivos acima do limite definido."""

    arquivo = tmp_path / "grande.txt"
    arquivo.write_text("A" * 100_001, encoding="utf-8")

    with pytest.raises(ValueError):
        ler_arquivo("grande.txt", raiz_autorizada=tmp_path)


@pytest.mark.skipif(os.name != "nt", reason="Teste específico do Windows")
def test_ler_arquivo_bloqueia_junction_externa(tmp_path):
    """Impede leitura de arquivos externos através de junctions."""

    projeto = tmp_path / "projeto"
    projeto.mkdir()

    externo = tmp_path / "privado"
    externo.mkdir()

    (externo / "segredo.txt").write_text(
        "informação confidencial",
        encoding="utf-8",
    )

    junction = projeto / "atalho"

    resultado = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(junction), str(externo)],
        capture_output=True,
        check=False,
    )

    if resultado.returncode != 0:
        pytest.skip("Não foi possível criar uma junction neste Windows.")

    with pytest.raises(PermissionError):
        ler_arquivo(
            "atalho/segredo.txt",
            raiz_autorizada=projeto,
        )


@pytest.mark.parametrize(
    "diretorio",
    [".git", ".venv", ".vscode", "data", "node_modules"],
)
def test_ler_arquivo_bloqueia_diretorios_sensiveis(tmp_path, diretorio):
    """Impede leitura de arquivos dentro de diretórios protegidos."""

    pasta = tmp_path / diretorio
    pasta.mkdir()

    arquivo = pasta / "segredo.txt"
    arquivo.write_text("informação privada", encoding="utf-8")

    with pytest.raises(PermissionError):
        ler_arquivo(
            f"{diretorio}/segredo.txt",
            raiz_autorizada=tmp_path,
        )
