"""¿Habría llegado a tiempo? Reproduce un plan Móstoles -> Nuevos Ministerios (llegar antes de las 9:00)
con las llegadas observadas de cada laborable del histórico (rodalies-observatorio).

Plan de Google Maps (jue 24/09/2026): C5 8:17 Móstoles Central -> Atocha 8:45, C10 8:51 -> N. Ministerios 8:57.
Aquí se prueba cada C5 de la mañana: se coge el primer tren real hacia Nuevos Ministerios
que pase por Atocha al menos TRANSBORDO min después de llegar.
"""
import pandas as pd
from analisis_margen import cargar

ORIGEN, ATOCHA, DESTINO = "Móstoles", "Madrid-Atocha Cercanías", "Madrid-Nuevos Ministerios"
TRANSBORDO = 4    # min andén a andén en Atocha (C5 -> vías de C10/C2/C7)
A_PIE_FINAL = 1   # min desde el andén hasta la calle
LIMITE = "09:00"

m = cargar()
m = m[m.laborable & (m.schedule_relationship == "SCHEDULED") & (m.service_date >= "2026-09-01")]
dias = m.groupby("service_date").trip_id.nunique()
m = m[m.service_date.isin(dias[dias > 1000].index)]
m["real"] = m.scheduled_arrival + pd.to_timedelta(m.delay_s, unit="s")

key = ["service_date", "trip_id"]
c5 = m[(m.linea == "C5") & (m.estacion == ORIGEN)][key + ["scheduled_arrival"]].merge(
    m[m.estacion == ATOCHA][key + ["scheduled_arrival", "real"]], on=key, suffixes=("_sale", "_atocha"))
c5 = c5[(c5.scheduled_arrival_atocha > c5.scheduled_arrival_sale)
        & c5.scheduled_arrival_sale.dt.strftime("%H:%M").between("07:30", "08:25")]

# trenes Atocha -> Nuevos Ministerios observados
at = m[m.estacion == ATOCHA][key + ["real"]].merge(
    m[m.estacion == DESTINO][key + ["real", "scheduled_arrival"]], on=key, suffixes=("_atocha", "_nm"))
at = at[at.real_nm > at.real_atocha]

filas = []
for _, v in c5.iterrows():
    cand = at[(at.service_date == v.service_date)
              & (at.real_atocha >= v.real + pd.Timedelta(minutes=TRANSBORDO))].sort_values("real_atocha")
    if cand.empty:
        continue
    llega = cand.iloc[0].real_nm + pd.Timedelta(minutes=A_PIE_FINAL)
    filas.append({"dia": v.service_date, "sale": v.scheduled_arrival_sale.strftime("%H:%M"),
                  "llega": llega.strftime("%H:%M"), "a_tiempo": llega.strftime("%H:%M") <= LIMITE})

r = pd.DataFrame(filas)
tabla = r.groupby("sale").agg(dias=("dia", "size"), a_tiempo=("a_tiempo", "sum"),
                              llegada_peor=("llega", "max"), llegada_mediana=("llega", lambda s: sorted(s)[len(s) // 2]))
print(f"Móstoles Central (C5) -> Nuevos Ministerios, llegar antes de las {LIMITE}, laborables 1-11 sep\n")
print(tabla.to_string())
