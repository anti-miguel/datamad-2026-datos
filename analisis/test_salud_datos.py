"""Pruebas de cobertura y atribución que afectan a las conclusiones de salud."""
import unittest
from analisis import salud_datos as s


class SaludTest(unittest.TestCase):
    def test_dia_cambio_hora_tiene_25_horas(self):
        a, b = s.limites_dia("2026-10-25")
        self.assertEqual(b - a, 90000)

    def test_cobertura_no_rellena_un_hueco(self):
        cobertura, huecos = s.cobertura_huecos([0, 30, 300], 0, 360, 30)
        self.assertEqual(cobertura, 90)
        self.assertEqual(max(y - x for x, y in huecos), 240)

    def test_flota_404_no_es_error_del_servicio_emt(self):
        fila = {"k": "flota", "err": "HTTP 404"}
        self.assertTrue(s.es_error(fila))
        self.assertFalse(s.error_relevante("emt", fila))

    def test_poll_con_error_anidado_cuenta(self):
        self.assertTrue(s.es_error({"k": "poll", "vp_err": "timeout"}))
        self.assertFalse(s.es_error({"k": "poll", "vp_err": None}))

    def test_ausencia_sin_prueba_no_se_atribuye_al_grabador(self):
        r = s.clasificar_hueco("emt", 0, 3600, [], False, False)
        self.assertEqual(r["clase"], "indeterminado")

    def test_error_mientras_otras_fuentes_graban_no_prueba_operador(self):
        r = s.clasificar_hueco("emt", 0, 3600, [], True, True)
        self.assertEqual(r["clase"], "operador_o_acceso")
        self.assertEqual(r["evidencia"], "inferencia")

    def test_hueco_catalogado_operador(self):
        reglas = [{"fuente": "emt", "inicio": 0, "fin": 3600, "tipo": "operador"}]
        r = s.clasificar_hueco("emt", 600, 1200, reglas, False, False)
        self.assertEqual(r["clase"], "operador")
        self.assertEqual(r["evidencia"], "confirmado en código")


if __name__ == "__main__":
    unittest.main()
