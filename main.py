import streamlit as st
import pandas as pd
from utils import *
from facebook_api import *

st.logo("https://avatars.githubusercontent.com/u/73341981?v=4", size="large")

st.title("Facebook Ads API explorer")
st.caption("Choisisez vos paramètres de recherche")

access_token = st.text_input("Token d'accès", "")

all_countries = eu_country_codes + ["US", "CA", "GB", "AU"]

with st.container(border=True):
    countries = st.multiselect("Pays", all_countries, default=["FR", "DE"])

search_terms = st.text_input("Termes de recherche", "cuisine")

ad_status = st.selectbox("Statut de l'annonce", ["ALL", "ACTIVE", "INACTIVE"])
date_min = st.date_input("Date de début de diffusion", None)
date_max = st.date_input("Date de fin de diffusion", None)
ad_type = st.selectbox("Type d'annonce", ["ALL", "FINANCIAL_PRODUCTS_AND_SERVICES_ADS", "EMPLOYMENT_ADS", "HOUSING_ADS", "POLITICAL_AND_ISSUE_ADS"])
media_type = st.selectbox("Type de média", ["ALL", "IMAGE", "MEME", "VIDEO"])
languages = st.multiselect("Langues contenu dans le post", ["en", "fr", "de", "es", "it"])
platforms = st.multiselect("Plateformes (All si vide)", ["FACEBOOK", "INSTAGRAM", "AUDIENCE_NETWORK", "MESSENGER"])
search_type = st.selectbox("Type de recherche", ["KEYWORD_UNORDERED", "KEYWORD_EXACT_PHRASE"])
unmask = st.checkbox("Afficher le contenu supprimé")

if st.button("Lancer la recherche"):
    if len(countries) == 0:
        st.error("Veuillez sélectionner au moins un pays.")
    else:
        params = {
            "ad_reached_countries": countries,
            "search_terms": search_terms,
            "ad_active_status": ad_status,
            "ad_type": ad_type,
            "media_type": media_type,
            "publisher_platforms": platforms,
            "search_type": search_type,
            "unmask_removed_content": unmask,
            "languages": languages,
        }

        if date_min:
            params["ad_delivery_date_min"] = date_min.strftime("%Y-%m-%d")
        if date_max:
            params["ad_delivery_date_max"] = date_max.strftime("%Y-%m-%d")

        response = sendRequest(params, access_token)

        if response is not None:
            st.success("Requête réussie.")
            
            if "data" in response and len(response["data"]) > 0:
                st.subheader(f"Résultats: {len(response['data'])} annonces trouvées")
                
                cols_per_row = 3
                
                for i in range(0, len(response["data"]), cols_per_row):
                    cols = st.columns(cols_per_row)
                    
                    for j in range(cols_per_row):
                        if i + j < len(response["data"]):
                            ad = response["data"][i + j]
                            with cols[j]:
                                with st.container(border=True):
                                    # Titre avec ID et nom de la page
                                    st.markdown(f"### {ad.get('page_name', 'N/A')}")
                                    
                                    # Informations principales
                                    st.markdown(f"**ID**: `{ad.get('id', 'N/A')}`")
                                    st.markdown(f"**Création**: {ad.get('ad_creation_time', 'N/A')}")
                                    
                                    # Dates de diffusion
                                    start_date = ad.get('ad_delivery_start_time', 'N/A')
                                    stop_date = ad.get('ad_delivery_stop_time', 'N/A')
                                    st.markdown(f"**Diffusion**: {start_date} → {stop_date if stop_date else 'En cours'}")
                                    
                                    # Portée
                                    total_reach = ad.get('eu_total_reach', 'N/A')
                                    st.markdown(f"**Portée**: {total_reach}")
                                    
                                    # Contenu de l'annonce
                                    if "ad_creative_bodies" in ad and ad["ad_creative_bodies"]:
                                        with st.expander("Contenu de l'annonce"):
                                            st.markdown(ad["ad_creative_bodies"][0])
                                    
                                    # Détails du lien
                                    link_info = []
                                    if "ad_creative_link_titles" in ad and ad["ad_creative_link_titles"]:
                                        link_info.append(f"**Titre**: {ad['ad_creative_link_titles'][0]}")
                                    if "ad_creative_link_captions" in ad and ad["ad_creative_link_captions"]:
                                        link_info.append(f"**Caption**: {ad['ad_creative_link_captions'][0]}")
                                    if "ad_creative_link_descriptions" in ad and ad["ad_creative_link_descriptions"]:
                                        link_info.append(f"**Description**: {ad['ad_creative_link_descriptions'][0]}")
                                    
                                    if link_info:
                                        with st.expander("Détails du lien"):
                                            for info in link_info:
                                                st.markdown(info)
                                    
                                    # Ciblage
                                    targeting_info = []
                                    
                                    # Langues
                                    if "languages" in ad and ad["languages"]:
                                        targeting_info.append(f"**Langues**: {', '.join(ad['languages'])}")
                                    
                                    # Plateformes
                                    if "publisher_platforms" in ad and ad["publisher_platforms"]:
                                        targeting_info.append(f"**Plateformes**: {', '.join(ad['publisher_platforms'])}")
                                    
                                    # Genre cible
                                    if "target_gender" in ad:
                                        targeting_info.append(f"**Genre cible**: {ad['target_gender']}")
                                    
                                    # Âges cibles
                                    if "target_ages" in ad and ad["target_ages"]:
                                        targeting_info.append(f"**Âges cibles**: {' - '.join(ad['target_ages'])}")
                                    
                                    # Lieux ciblés
                                    if "target_locations" in ad and ad["target_locations"]:
                                        locations = []
                                        for loc in ad["target_locations"]:
                                            locations.append(f"{loc.get('name', 'N/A')} ({loc.get('type', 'N/A')})")
                                        targeting_info.append(f"**Lieux**: {', '.join(locations)}")
                                    
                                    if targeting_info:
                                        with st.expander("Ciblage"):
                                            for info in targeting_info:
                                                st.markdown(info)
                                    
                                    # Démographie
                                    if "age_country_gender_reach_breakdown" in ad and ad["age_country_gender_reach_breakdown"]:
                                        with st.expander("Démographie"):
                                            for country_data in ad["age_country_gender_reach_breakdown"]:
                                                st.markdown(f"**Pays**: {country_data.get('country', 'N/A')}")
                                                
                                                if "age_gender_breakdowns" in country_data:
                                                    # Créer un DataFrame pour l'affichage des données démographiques
                                                    demo_data = []
                                                    for breakdown in country_data["age_gender_breakdowns"]:
                                                        demo_data.append({
                                                            "Âge": breakdown.get("age_range", "N/A"),
                                                            "Homme": breakdown.get("male", 0),
                                                            "Femme": breakdown.get("female", 0),
                                                            "Inconnu": breakdown.get("unknown", 0)
                                                        })
                                                    
                                                    if demo_data:
                                                        df = pd.DataFrame(demo_data)
                                                        st.dataframe(df, use_container_width=True)
                                    
                                    # Lien vers le snapshot
                                    if "ad_snapshot_url" in ad:
                                        st.markdown(f"[Voir l'annonce sur Facebook]({ad['ad_snapshot_url']})")

            with st.expander("Données brutes (JSON)"):
                st.json(response)





