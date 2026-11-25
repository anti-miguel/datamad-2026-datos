"""Verifica aislamiento de las copias del portal y preservación de las salidas históricas.

Uso desde la raíz: python analisis/verificar_refresh.py
"""
import builtins
from pathlib import Path
import subprocess
from unittest.mock import patch

import cruce_catalogo


def main():
    datos = Path("datos").resolve()
    originales = {p: p.read_bytes() for p in Path("datos/catalogo_cm").iterdir() if p.is_file()}
    abrir = builtins.open

    def solo_lectura(p, modo="r", *args, **kwargs):
        if isinstance(p, (str, bytes, Path)) and datos in Path(p).resolve().parents and any(c in modo for c in "wax+"):
            raise AssertionError(f"Intento de escritura en datos/: {p}")
        return abrir(p, modo, *args, **kwargs)

    with patch("socket.socket", side_effect=AssertionError("Intento de acceso a red")), patch("builtins.open", side_effect=solo_lectura):
        cat, meta = cruce_catalogo.catalogo()
        assert len(cat) == len(meta) == 4
        with patch.object(cruce_catalogo, "CM", "analisis/resultados/copia_inexistente_para_verificacion"):
            try:
                cruce_catalogo.catalogo()
            except FileNotFoundError:
                pass
            else:
                raise AssertionError("Una copia ausente debe fallar sin descargar")
    assert all(p.read_bytes() == b for p, b in originales.items())
    historicos = ["fiabilidad.csv", "fiabilidad_validacion.txt", "fiabilidad_interurbanos_estabilidad.csv",
                  "cruce_catalogo.txt", "cruce_catalogo_emt_lineas.csv", "cruce_catalogo_renfe_estaciones.csv"]
    subprocess.run(["git", "diff", "--exit-code", "HEAD", "--", *[f"analisis/resultados/{n}" for n in historicos]], check=True)
    cambios = subprocess.check_output(["git", "diff", "--name-only", "HEAD"], text=True).splitlines()
    assert all(p.startswith("analisis/") for p in cambios), cambios
    print("Comprobado ejecutando: cuatro datasets locales leídos con red y escrituras en datos/ bloqueadas.")
    print("Comprobado ejecutando: copia ausente falla sin descargar; copias locales intactas byte a byte.")
    print("Comprobado ejecutando: seis salidas históricas intactas frente a HEAD; cambios rastreados solo bajo analisis/.")


if __name__ == "__main__":
    main()
