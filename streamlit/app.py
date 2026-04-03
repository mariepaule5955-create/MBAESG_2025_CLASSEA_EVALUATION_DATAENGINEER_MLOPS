# ============================================================
# APPLICATION STREAMLIT — House Price Predictor
# À déployer dans Snowflake via : Snowflake > Streamlit > New App
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
from snowflake.snowpark.context import get_active_session
from snowflake.ml.registry import Registry

# -------------------------------------------------------------------
# Configuration de la page
# -------------------------------------------------------------------
st.set_page_config(
    page_title="🏠 House Price Predictor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------
# CSS personnalisé
# -------------------------------------------------------------------
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1565C0;
        text-align: center;
        padding: 1rem 0 0.5rem 0;
    }
    .sub-header {
        text-align: center;
        color: #546E7A;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .prediction-box {
        background: linear-gradient(135deg, #1565C0, #0D47A1);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        color: white;
        margin: 1rem 0;
    }
    .prediction-price {
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -1px;
    }
    .metric-card {
        background: #F5F9FF;
        border-left: 4px solid #1565C0;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0;
    }
    .section-title {
        color: #1565C0;
        font-weight: 600;
        font-size: 1.1rem;
        border-bottom: 2px solid #E3F2FD;
        padding-bottom: 0.3rem;
        margin: 1rem 0 0.8rem 0;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# Connexion Snowflake et chargement du modèle
# -------------------------------------------------------------------
@st.cache_resource(show_spinner="Connexion à Snowflake...")
def get_model():
    session = get_active_session()
    registry = Registry(
        session=session,
        database_name='HOUSE_PRICE_DB',
        schema_name='ML'
    )
    model = registry.get_model('HOUSE_PRICE_RF_MODEL').version('V1')
    return session, model

try:
    session, model = get_model()
    model_loaded = True
except Exception as e:
    model_loaded = False
    st.error(f"❌ Erreur de connexion : {e}")

# -------------------------------------------------------------------
# Header
# -------------------------------------------------------------------
st.markdown('<div class="main-header">🏠 House Price Predictor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Estimez le prix de votre bien immobilier grâce à notre modèle ML entraîné sur Snowflake</div>', unsafe_allow_html=True)

if model_loaded:
    st.success("✅ Modèle chargé depuis le Snowflake Model Registry (HOUSE_PRICE_RF_MODEL V1)")

st.divider()

# -------------------------------------------------------------------
# Layout principal : formulaire + résultats
# -------------------------------------------------------------------
col_form, col_result = st.columns([1, 1], gap="large")

with col_form:
    st.markdown('<div class="section-title">📐 Caractéristiques de la maison</div>', unsafe_allow_html=True)

    # --- Surfaces & Pièces ---
    c1, c2 = st.columns(2)
    with c1:
        area = st.number_input(
            "Surface (m²)", min_value=100, max_value=20000, value=3000, step=100,
            help="Surface habitable totale en mètres carrés"
        )
        bedrooms = st.slider("Chambres 🛏️", 1, 6, 3)
        bathrooms = st.slider("Salles de bain 🚿", 1, 4, 2)

    with c2:
        stories = st.slider("Étages 🏢", 1, 4, 2)
        parking = st.slider("Places parking 🚗", 0, 3, 1)
        furnishing_label = st.selectbox(
            "Ameublement 🛋️",
            ["Meublée", "Semi-meublée", "Non meublée"],
            index=0
        )
        furnishing_map = {"Meublée": 2, "Semi-meublée": 1, "Non meublée": 0}
        furnishingstatus = furnishing_map[furnishing_label]

    st.markdown('<div class="section-title">✨ Équipements & Localisation</div>', unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        mainroad       = 1 if st.checkbox("Route principale 🛣️", value=True)  else 0
        airconditioning = 1 if st.checkbox("Climatisation ❄️", value=True)   else 0
        guestroom      = 1 if st.checkbox("Chambre d'amis 🏨", value=False)  else 0

    with c4:
        prefarea        = 1 if st.checkbox("Zone privilégiée ⭐", value=False) else 0
        basement        = 1 if st.checkbox("Sous-sol 🏚️", value=False)        else 0
        hotwaterheating = 1 if st.checkbox("Chauffe-eau ♨️", value=False)     else 0

    # Features dérivées
    room_ratio      = bathrooms / bedrooms if bedrooms > 0 else 1.0
    total_amenities = guestroom + basement + hotwaterheating + airconditioning

    predict_button = st.button("🔮 Estimer le prix", type="primary", use_container_width=True)

# -------------------------------------------------------------------
# Résultats
# -------------------------------------------------------------------
with col_result:
    st.markdown('<div class="section-title">📊 Résultat de l\'estimation</div>', unsafe_allow_html=True)

    if predict_button and model_loaded:
        input_data = pd.DataFrame([{
            'area'             : float(area),
            'bedrooms'         : int(bedrooms),
            'bathrooms'        : int(bathrooms),
            'stories'          : int(stories),
            'mainroad'         : int(mainroad),
            'guestroom'        : int(guestroom),
            'basement'         : int(basement),
            'hotwaterheating'  : int(hotwaterheating),
            'airconditioning'  : int(airconditioning),
            'parking'          : int(parking),
            'prefarea'         : int(prefarea),
            'furnishingstatus' : int(furnishingstatus),
            'room_ratio'       : float(room_ratio),
            'total_amenities'  : int(total_amenities)
        }])

        with st.spinner("Calcul en cours..."):
            try:
                prediction = model.run(input_data, function_name='predict')
                pred_price = float(prediction[0]) if hasattr(prediction, '__iter__') else float(prediction)

                # Encadré principal
                st.markdown(f"""
                <div class="prediction-box">
                    <div style="font-size:1rem; opacity:0.85; margin-bottom:0.5rem">Prix estimé</div>
                    <div class="prediction-price">{pred_price:,.0f} ₹</div>
                    <div style="font-size:0.9rem; opacity:0.7; margin-top:0.5rem">
                        Modèle Random Forest — R² = 0.88
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Métriques de la maison
                st.markdown('<div class="section-title">📌 Résumé de votre bien</div>', unsafe_allow_html=True)

                m1, m2, m3 = st.columns(3)
                m1.metric("Surface", f"{area} m²")
                m2.metric("Pièces", f"{bedrooms} ch. / {bathrooms} sdb")
                m3.metric("Étages", f"{stories}")

                m4, m5, m6 = st.columns(3)
                m4.metric("Parking", f"{parking} place(s)")
                m5.metric("Ameublement", furnishing_label)
                m6.metric("Équipements", f"{total_amenities}/4")

                # Sauvegarde en base
                input_data['PREDICTED_PRICE'] = pred_price
                input_data.columns = [c.upper() for c in input_data.columns]
                snow_df = session.create_dataframe(input_data)
                snow_df.write.save_as_table(
                    'HOUSE_PRICE_DB.ML.STREAMLIT_PREDICTIONS',
                    mode='append'
                )
                st.caption("✅ Prédiction sauvegardée dans HOUSE_PRICE_DB.ML.STREAMLIT_PREDICTIONS")

            except Exception as e:
                st.error(f"❌ Erreur lors de la prédiction : {e}")
                st.info("💡 Assurez-vous que le modèle est bien enregistré dans le registry (Étape 8 du notebook)")

    elif not model_loaded:
        st.warning("⚠️ Le modèle n'est pas chargé. Vérifiez la connexion Snowflake.")
    else:
        st.info("👆 Renseignez les caractéristiques de la maison et cliquez sur **Estimer le prix**")

        # Exemples de référence
        st.markdown('<div class="section-title">📚 Exemples de référence</div>', unsafe_allow_html=True)
        examples = pd.DataFrame({
            'Type': ['Studio basique', 'Maison moyenne', 'Villa premium'],
            'Surface': ['1800 m²', '3000 m²', '5500 m²'],
            'Chambres': [2, 3, 5],
            'Prix estimé (₹)': ['~2 500 000', '~4 500 000', '~9 000 000']
        })
        st.table(examples)

# -------------------------------------------------------------------
# Section : Historique des prédictions
# -------------------------------------------------------------------
st.divider()
st.markdown('<div class="section-title">📜 Historique des estimations (session)</div>', unsafe_allow_html=True)

if model_loaded:
    try:
        history_df = session.table('HOUSE_PRICE_DB.ML.STREAMLIT_PREDICTIONS')\
                            .select('AREA', 'BEDROOMS', 'BATHROOMS', 'STORIES',
                                    'AIRCONDITIONING', 'PREFAREA', 'PREDICTED_PRICE')\
                            .limit(10)\
                            .to_pandas()
        if not history_df.empty:
            history_df.columns = [c.lower() for c in history_df.columns]
            history_df['predicted_price'] = history_df['predicted_price'].apply(lambda x: f'{x:,.0f} ₹')
            st.dataframe(history_df, use_container_width=True)
        else:
            st.info("Aucune estimation réalisée pour l'instant.")
    except:
        st.info("Aucune estimation réalisée pour l'instant.")

# -------------------------------------------------------------------
# Footer
# -------------------------------------------------------------------
st.divider()
st.markdown("""
<div style="text-align:center; color:#90A4AE; font-size:0.85rem">
    🏠 House Price Predictor — Construit avec Snowflake ML, Snowpark & Streamlit<br>
    Modèle : Random Forest Regressor | Entraîné sur 545 maisons | R² ≈ 0.88
</div>
""", unsafe_allow_html=True)
