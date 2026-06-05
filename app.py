# Smart Farmer Assistant
# Save as app.py and run: streamlit run app.py

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from deep_translator import GoogleTranslator

st.set_page_config(page_title="Smart Farmer Assistant", page_icon="🌾", layout="wide")

languages = {"English":"en","Hindi":"hi","Kannada":"kn"}
selected_language = st.sidebar.selectbox("Select Language", list(languages.keys()))
lang_code = languages[selected_language]

manual_translations = {
    "kn":{"Black":"ಕಪ್ಪು ಮಣ್ಣು","Red":"ಕೆಂಪು ಮಣ್ಣು","Loamy":"ಮರಳು ಮಿಶ್ರ ಮಣ್ಣು","Clay":"ಜೇಡಿಮಣ್ಣು",
          "Kharif":"ಖರೀಫ್","Rabi":"ರಬಿ","Summer":"ಬೇಸಿಗೆ","Low":"ಕಡಿಮೆ","Medium":"ಮಧ್ಯಮ","High":"ಹೆಚ್ಚು",
          "Cotton":"ಹತ್ತಿ","Soybean":"ಸೋಯಾಬೀನ್","Groundnut":"ಕಡಲೆಕಾಯಿ","Millets":"ಸಿರಿಧಾನ್ಯಗಳು",
          "Wheat":"ಗೋಧಿ","Sugarcane":"ಕಬ್ಬು","Rice":"ಅಕ್ಕಿ","Jute":"ಸೆಣಬು"},
    "hi":{"Black":"काली मिट्टी","Red":"लाल मिट्टी","Loamy":"दोमट मिट्टी","Clay":"चिकनी मिट्टी",
          "Kharif":"खरीफ","Rabi":"रबी","Summer":"गर्मी","Low":"कम","Medium":"मध्यम","High":"अधिक",
          "Cotton":"कपास","Soybean":"सोयाबीन","Groundnut":"मूंगफली","Millets":"मोटा अनाज",
          "Wheat":"गेहूं","Sugarcane":"गन्ना","Rice":"चावल","Jute":"जूट"}
}

@st.cache_data
def translate_text(text, target_lang):
    if target_lang == "en":
        return text
    if target_lang in manual_translations and text in manual_translations[target_lang]:
        return manual_translations[target_lang][text]
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except:
        return text

def tr(text):
    return translate_text(text, lang_code)

DATA_FILE = "farmer_records.csv"
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Date","Farmer","Soil","Season","Crop","Area","Fertilizer","Revenue","Profit"]).to_csv(DATA_FILE,index=False)

crop_data = {
    "Black":["Cotton","Soybean"],
    "Red":["Groundnut","Millets"],
    "Loamy":["Wheat","Sugarcane"],
    "Clay":["Rice","Jute"]
}

st.title(tr("🌾 Smart Farmer Assistant"))
st.write(tr("Helping Rural Farmers with Smart Agricultural Decisions"))

menu = st.sidebar.radio(tr("Choose Service"),
                        [tr("Crop Recommendation"),tr("Fertilizer Calculator"),
                         tr("Profit Estimator"),tr("Farmer Records")])

if menu == tr("Crop Recommendation"):
    st.header(tr("Crop Recommendation"))
    st.text_input(tr("Farmer Name"))
    soil_map = {k: tr(k) for k in ["Black","Red","Loamy","Clay"]}
    soil_display = st.selectbox(tr("Soil Type"), list(soil_map.values()))
    soil = {v:k for k,v in soil_map.items()}[soil_display]
    st.selectbox(tr("Season"), [tr("Kharif"), tr("Rabi"), tr("Summer")])
    st.selectbox(tr("Water Availability"), [tr("Low"), tr("Medium"), tr("High")])

    if st.button(tr("Recommend Crop")):
        crops = [tr(c) for c in crop_data[soil]]
        st.success(tr("Recommended Crops") + ": " + ", ".join(crops))

elif menu == tr("Fertilizer Calculator"):
    st.header(tr("Fertilizer Calculator"))
    area = st.number_input(tr("Land Area (Acres)"), min_value=0.1, value=1.0)
    if st.button(tr("Calculate Fertilizer")):
        st.success(tr("Required Fertilizer") + f": {area*50:.1f} kg")

elif menu == tr("Profit Estimator"):
    st.header(tr("Profit Estimator"))
    farmer = st.text_input(tr("Farmer Name"))
    soil = st.selectbox(tr("Soil Type"), ["Black","Red","Loamy","Clay"])
    season = st.selectbox(tr("Season"), ["Kharif","Rabi","Summer"])
    area = st.number_input(tr("Land Area"), min_value=0.1, value=1.0)
    cost = st.number_input(tr("Cultivation Cost"), min_value=0.0)
    yield_kg = st.number_input(tr("Expected Yield (kg)"), min_value=0.0)
    price = st.number_input(tr("Market Price per kg"), min_value=0.0)

    if st.button(tr("Estimate Profit")):
        revenue = yield_kg * price
        profit = revenue - cost
        st.metric(tr("Revenue"), f"₹{revenue:,.2f}")
        st.metric(tr("Profit"), f"₹{profit:,.2f}")

        record = pd.DataFrame({
            "Date":[datetime.now()],"Farmer":[farmer],"Soil":[soil],
            "Season":[season],"Crop":[", ".join(crop_data[soil])],
            "Area":[area],"Fertilizer":[area*50],"Revenue":[revenue],"Profit":[profit]
        })
        old = pd.read_csv(DATA_FILE)
        pd.concat([old,record],ignore_index=True).to_csv(DATA_FILE,index=False)
        st.success(tr("Record Saved Successfully"))

else:
    st.header(tr("Farmer Records"))
    data = pd.read_csv(DATA_FILE)
    st.dataframe(data, use_container_width=True)
    st.download_button(tr("Download CSV"), data.to_csv(index=False),
                       "farmer_records.csv", "text/csv")
