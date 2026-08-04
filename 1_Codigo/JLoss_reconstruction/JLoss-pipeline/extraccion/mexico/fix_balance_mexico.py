"""
fix_balance_mexico.py
---------------------
Repara el balance_mexico.csv YA generado: unifica los nombres de banco duplicados
(typos y variantes banco_X / X / X_banco que la CNBV fue cambiando en el tiempo)
a un slug canonico unico, sin volver a extraer.

Las variantes son DISJUNTAS en el tiempo (renombres), por lo que reetiquetar no
genera colisiones; aun asi se incluye una red de seguridad que coalesce filas
(bankname, date) duplicadas tomando el primer valor no-nulo por columna.

Uso:  python fix_balance_mexico.py [ruta_csv]   (default: balance_mexico.csv)
Salida: respalda el original como balance_mexico_raw.csv y sobreescribe balance_mexico.csv
"""
import sys
import shutil
import pandas as pd

# --- Diccionario canonico: variante -> nombre unico. Confirmado por solape temporal
#     (disjunto) y continuidad de activos en el punto de empalme. ------------------
BANK_ALIASES = {
    # typos / prefijos del mismo banco
    "bicentenario": "banco_bicentenario",
    "bicentenrio": "banco_bicentenario",            # typo
    "banco_bicentenario": "banco_bicentenario",
    "donde": "banco_donde",
    "donde_banco": "banco_donde",
    "banco_donde": "banco_donde",
    "uala": "banco_uala",
    "banco_uala": "banco_uala",
    "covalto": "banco_covalto",
    "banco_covalto": "banco_covalto",
    "forjadores": "banco_forjadores",
    "banco_forjadores": "banco_forjadores",
    "banfeliz_antes_forjadores": "banco_forjadores",  # renombre declarado
    "finterra": "banco_finterra",
    "banco_finterra": "banco_finterra",
    "intercam": "intercam_banco",
    "inter_banco": "intercam_banco",                 # mismo banco (empalme 19.9k->18.5k)
    "keb_hana_bank": "keb_hana_mexico",
    "keb_hana_mexico": "keb_hana_mexico",
    "ubs": "ubs_bank",
    "ubs_bank": "ubs_bank",
    "bank_of_tokio_mitsubishi_ufj": "bank_of_tokyo_mitsubishi_ufj",   # typo tokio->tokyo
    "bank_of_tokyo_mitsubishi_ufj": "bank_of_tokyo_mitsubishi_ufj",
}


def canonical_bankname(name):
    """Devuelve el slug canonico de un banco mexicano (idempotente)."""
    return BANK_ALIASES.get(str(name).strip(), str(name).strip())


def fix_balance(path="balance_mexico.csv"):
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    n0 = df["bankname"].nunique()

    df["bankname"] = df["bankname"].map(canonical_bankname)

    # red de seguridad: coalescer filas (bankname, date) que hayan quedado duplicadas
    dup_mask = df.duplicated(subset=["bankname", "date"], keep=False)
    n_dups = int(dup_mask.sum())
    if n_dups:
        # tomar el primer valor NO-nulo por columna dentro de cada (bankname, date)
        df = (df.sort_values(["bankname", "date"])
                .groupby(["bankname", "date"], as_index=False)
                .first())
        print(f"  aviso: {n_dups} filas (bankname,date) duplicadas tras unificar -> coalescidas")

    # reconstruir year/month por consistencia
    if "year" in df.columns:
        df["year"] = df["date"].dt.year
    if "month" in df.columns:
        df["month"] = df["date"].dt.month

    df = df.sort_values(["bankname", "date"]).reset_index(drop=True)
    n1 = df["bankname"].nunique()

    shutil.copyfile(path, path.replace(".csv", "_raw.csv"))
    df.to_csv(path, index=False)
    print(f"OK: bancos {n0} -> {n1} ({n0 - n1} fusionados). "
          f"Original respaldado en {path.replace('.csv', '_raw.csv')}")
    return df


if __name__ == "__main__":
    fix_balance(sys.argv[1] if len(sys.argv) > 1 else "balance_mexico.csv")