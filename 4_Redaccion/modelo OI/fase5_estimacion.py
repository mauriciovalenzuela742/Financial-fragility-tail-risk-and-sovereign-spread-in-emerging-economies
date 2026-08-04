"""
Fase V - Pipeline de estimacion (convencion GaR; apuntar a datos reales).
Lee un panel CSV con columnas: country,time,EMBI,JLoss,GaR,HHI,debt[,PD_bank,Lerner,gfac,...]
donde GaR = cuantil bajo del crecimiento (Growth-at-Risk, negativo en la cola).

Especificacion principal (Fase IV, convencion GaR):
  EMBI_it = a_i + d_t + b1 JLoss + b2 GaR + b3 (JLoss x GaR) + b4 (JLoss x GaR x HHI)
            + (interacciones de orden inferior) + g' X + e_it
Predicciones firmadas:  b1>0 ,  b2<0 ,  b3<0 ,  b4<0.
  (b3<0 y b4<0 SON la complementariedad y su amplificacion: como GaR baja en la cola,
   un coeficiente negativo sobre el producto refuerza el spread cuando ambos empeoran.)

Requiere: pandas, linearmodels, statsmodels.
Uso: python fase5_estimacion.py panel_template.csv
"""
import sys, pandas as pd
from linearmodels.panel import PanelOLS
import statsmodels.formula.api as smf

path = sys.argv[1] if len(sys.argv)>1 else 'panel_template.csv'
df = pd.read_csv(path)

# --- construir interacciones ---
df['JL_G']     = df.JLoss*df.GaR
df['JL_G_HHI'] = df.JLoss*df.GaR*df.HHI
df['JL_HHI']   = df.JLoss*df.HHI
df['G_HHI']    = df.GaR*df.HHI
pdf = df.set_index(['country','time'])

# --- (1) especificacion principal: TWFE, SE agrupados por pais ---
f_main = ('EMBI ~ JLoss + GaR + JL_G + JL_G_HHI + JL_HHI + G_HHI + debt '
          '+ EntityEffects + TimeEffects')
res = PanelOLS.from_formula(f_main, pdf).fit(cov_type='clustered', cluster_entity=True)
print(res.summary.tables[1])
print("\nPredicciones firmadas:  b1(JLoss)>0 , b2(GaR)<0 , b3(JL_G)<0 , b4(JL_G_HHI)<0")

# robustez SE: Driscoll-Kraay (dependencia cross-section)
res_dk = PanelOLS.from_formula(f_main, pdf).fit(cov_type='kernel')
print("Driscoll-Kraay  JL_G=%+.3f (t=%.2f)  JL_G_HHI=%+.3f (t=%.2f)"
      % (res_dk.params['JL_G'], res_dk.tstats['JL_G'],
         res_dk.params['JL_G_HHI'], res_dk.tstats['JL_G_HHI']))

# efecto marginal de la complementariedad segun HHI (Prop. 4): dEMBI/dJLoss dGaR = b3 + b4*HHI
me = lambda h: res.params['JL_G'] + res.params['JL_G_HHI']*h
print("\nd2EMBI/dJLoss dGaR :  HHI=0.08 -> %.3f ;  HHI=0.30 -> %.3f  (mas negativo si concentrado)"
      % (me(0.08), me(0.30)))

# --- (2) H1: U-shape de la fragilidad individual (si hay PD bancaria y Lerner) ---
if {'PD_bank','Lerner'}.issubset(df.columns):
    df['Lerner2']=df.Lerner**2
    h1=smf.ols('PD_bank ~ Lerner + Lerner2 + C(country) + C(time)', df).fit()
    print("\nH1 (U-shape): Lerner=%+.3f Lerner^2=%+.3f (U si Lerner^2>0)"
          % (h1.params['Lerner'], h1.params['Lerner2']))

# --- (3) H3: traspaso JLoss->GaR mas profundo si concentrado (quantile reg del crecimiento) ---
if {'growth','gfac'}.issubset(df.columns):
    q=smf.quantreg('growth ~ JLoss + JL_HHI + gfac + C(country)', df).fit(q=0.10)
    print("\nH3 (tau=0.10): JLoss=%+.3f  JLoss*HHI=%+.3f  (ambos <0 => crunch mas fuerte si concentrado)"
          % (q.params['JLoss'], q.params['JL_HHI']))

print("\nNota identificacion: usar rezagos (JLoss_{t-1}, GaR_{t-1}) o instrumentos de "
      "competencia (shocks de entrada/desregulacion) si hay simultaneidad doom-loop.")
print("Nota convencion: si tus datos traen D=-GaR en vez de GaR, los signos de b2,b3,b4 se invierten.")
