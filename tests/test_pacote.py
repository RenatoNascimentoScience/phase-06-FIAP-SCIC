import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile


RAIZ = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("preparar_entrega", RAIZ / "scripts/preparar_entrega.py")
pacote = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pacote)


class TestPacote(unittest.TestCase):
    def preparar_exemplo_incompleto(self, raiz):
        for nome in pacote.OBRIGATORIOS:
            (raiz / nome).write_text("Arquivo de teste.\n", encoding="utf-8")
        (raiz / "codigo_fonte.py").write_text(
            "def main():\n    funcionalidade_em_desenvolvimento('teste')\n", encoding="utf-8")
        (raiz / "link_video.txt").write_text("PENDENTE\n", encoding="utf-8")

    def test_detecta_menu_pendente_e_link_invalido(self):
        with tempfile.TemporaryDirectory(prefix="scic-pacote-") as temporario:
            raiz = Path(temporario)
            self.preparar_exemplo_incompleto(raiz)
            pendencias = pacote.pendencias_entrega(raiz)
            self.assertTrue(any("menu" in frase for frase in pendencias))
            self.assertTrue(any("YouTube" in frase for frase in pendencias))

    def test_pacote_final_bloqueado_enquanto_incompleto(self):
        with tempfile.TemporaryDirectory(prefix="scic-pacote-") as temporario:
            raiz = Path(temporario)
            self.preparar_exemplo_incompleto(raiz)
            destino = raiz / "final.zip"
            with self.assertRaises(ValueError):
                pacote.preparar_pacote(raiz, destino)
            self.assertFalse(destino.exists())

    def test_helper_provisorio_sem_chamada_nao_bloqueia_menu_integrado(self):
        with tempfile.TemporaryDirectory(prefix="scic-pacote-") as temporario:
            raiz = Path(temporario)
            self.preparar_exemplo_incompleto(raiz)
            (raiz / "codigo_fonte.py").write_text(
                "def funcionalidade_em_desenvolvimento(nome):\n    pass\n\ndef main():\n    pass\n", encoding="utf-8")
            (raiz / "link_video.txt").write_text("https://youtu.be/abcdefghijk\n", encoding="utf-8")
            self.assertEqual(pacote.pendencias_entrega(raiz), [])

    def test_candidato_inclui_fontes_e_pendencias_sem_caches_ou_historico(self):
        with tempfile.TemporaryDirectory(prefix="scic-pacote-") as temporario:
            destino = Path(temporario) / "candidato.zip"
            pacote.preparar_pacote(RAIZ, destino, candidato=True)
            with zipfile.ZipFile(destino) as arquivo:
                self.assertIsNone(arquivo.testzip())
                nomes = arquivo.namelist()
                for nome in pacote.OBRIGATORIOS:
                    self.assertIn("SCIC_Aurora_Siger/" + nome, nomes)
                self.assertIn("SCIC_Aurora_Siger/src/alertas.py", nomes)
                self.assertIn("SCIC_Aurora_Siger/PENDENCIAS_ENTREGA.txt", nomes)
                self.assertFalse(any(".git/" in nome or "__pycache__" in nome or ".venv" in nome for nome in nomes))
                self.assertEqual(arquivo.read("SCIC_Aurora_Siger/codigo_fonte.py"), (RAIZ / "codigo_fonte.py").read_bytes())
                self.assertEqual(arquivo.read("SCIC_Aurora_Siger/dados_aurora_siger.csv"), (RAIZ / "dados_aurora_siger.csv").read_bytes())


if __name__ == "__main__":
    unittest.main()
