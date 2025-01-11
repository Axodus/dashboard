import streamlit as st


def logo():
    logo_img = "./frontend/visualization/img/logo.png"
    icon = "./frontend/visualization/img/favicon.png"
    st.logo(
            logo_img,
            link="http://localhost:8501",
            icon_image=icon,
            )
