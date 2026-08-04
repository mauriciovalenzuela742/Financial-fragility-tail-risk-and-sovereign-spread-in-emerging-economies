import sys; sys.path.insert(0, "individuals")
import fci_engine as fe

paises = ["BULGARIA","CHINA","HUNGARY","INDIA","INDONESIA","MALAYSIA",
          "PAKISTAN","PHILIPPINES","POLAND","RUSSIA","SOUTHAFRICA",
          "SOUTHKOREA","THAILAND","TURKEY"]   # excluye ARGENTINA/SAUDIARABIA

for pais in paises:
    try:
        df = fe.compute_fci(
            country_dir=f"individuals/{pais}", country=pais,
            ref_dir="individuals/US", ref_country="US",
            initial="1990-01-01",
            final="2026-05-31",   # tope = ultimo mes con rEER real (ver paso 3)
        )
        print(pais, "OK", df.shape, df.DATES.max().date())
    except Exception as e:
        print(pais, "ERROR", e)