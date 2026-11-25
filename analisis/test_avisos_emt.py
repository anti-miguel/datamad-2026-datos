"""Casos sintéticos: identidad de líneas, medida, calendario y contaminación."""
import unittest
from collections import Counter

import pandas as pd

from analisis import avisos_emt as a


class AvisosEmtTest(unittest.TestCase):
    def test_no_confunde_lineas_cero_con_lineas_ordinarias(self):
        nombres = {"1", "2", "001", "002", "3", "C03"}
        self.assertEqual(a.normalizar_linea("001", nombres), "001")
        self.assertEqual(a.normalizar_linea("1", nombres), "1")
        self.assertEqual(a.normalizar_linea("003", nombres), "3")
        self.assertEqual(a.normalizar_linea("C03", nombres), "C03")

    def test_cierre_invalido_no_se_convierte_en_llegada(self):
        filas = [
            {"t": 1000, "s": "82", "a": [["1", 5, 300, 900, 0, 0, "0", "A"]]},
            {"t": 1180, "s": "82", "a": [["1", 5, 60, 200, 0, 0, "3", "A"]]},
            {"t": 1000, "s": "83", "a": [["2", 6, 300, 900, 0, 0, "0", "B"]]},
            {"t": 1180, "s": "83", "a": [["2", 6, 60, 200, 0, 0, "0", "B"]]},
            {"t": 1000, "s": "84", "a": [["3", 7, 999999, 200, 0, 0, "0", "C"]]},
        ]
        d = a.predicciones_dia(filas, {"1", "2", "3"}, Counter())
        self.assertEqual(d.linea.tolist(), ["2"])
        self.assertEqual(d.ok.tolist(), [True])
        self.assertEqual(d.t.tolist(), [1000])

    def test_placebo_conserva_hora_local_al_cambiar_hora(self):
        inicio = pd.Timestamp("2026-10-20 18:00", tz="Europe/Madrid")
        fin = pd.Timestamp("2026-10-20 20:00", tz="Europe/Madrid")
        nuevo, _ = a.desplazar(inicio, fin, 7)
        self.assertEqual(nuevo.isoformat(), "2026-10-27T18:00:00+01:00")
        self.assertEqual(nuevo.timestamp() - inicio.timestamp(), 7 * 86400 + 3600)

    def test_ventana_tocando_extremo_no_esta_contaminada(self):
        intervalos = {"1": [(100, 200), (300, 400)]}
        self.assertFalse(a.contaminada("1", 200, 300, intervalos))
        self.assertTrue(a.contaminada("1", 199, 300, intervalos))

    def test_hora_repetida_se_resuelve_a_primera_ocurrencia(self):
        inicio = pd.Timestamp("2026-10-18 02:30", tz="Europe/Madrid")
        fin = pd.Timestamp("2026-10-18 03:30", tz="Europe/Madrid")
        nuevo, nuevo_fin = a.desplazar(inicio, fin, 7)
        self.assertEqual(nuevo.isoformat(), "2026-10-25T02:30:00+02:00")
        self.assertEqual(nuevo_fin.isoformat(), "2026-10-25T03:30:00+01:00")

    def test_bootstrap_mantiene_juntas_las_lineas_del_mismo_aviso(self):
        d = pd.DataFrame({"guid": ["aviso-unico", "aviso-unico"], "diferencia_pp": [-10., 10.],
                          "p_control": [.5, .5], "p_aviso": [.4, .6], "p_placebo": [.5, .5],
                          "n_aviso": [20, 20], "n_control": [40, 40], "n_placebo": [20, 20]})
        s = a.estadistica(d, "diferencia_pp", 100, 1)
        self.assertEqual(s["pares"], 2)
        self.assertEqual(s["avisos"], 1)
        self.assertEqual(s["ic95_pp"], [0., 0.])


if __name__ == "__main__":
    unittest.main()
