import streamlit as st

from frontend.st_utils import auth_system
from frontend.visualization.logo import logo

logo()


def main():
    # readme section
    st.html('''
        <img src="frontend/visualization/img/favicon.png" alt="Favicon" width="25">
        <h1>Axodus Dashboard</h1>
        <p>
            Hummingbot Dashboard is an open source application that helps you create, backtest, and optimize
            various types of algo trading strategies. Afterwards, you can deploy them as
            <a href='http://hummingbot.org' target='_blank'>Hummingbot</a>.
        </p>
        <hr>
        <h2>Watch the Hummingbot Dashboard Tutorial!</h2> ''')
    st.video("https://youtu.be/7eHiMPRBQLQ?si=PAvCq0D5QDZz1h1D")
    st.html('''
        <h2>Feedback and Issues</h2>
        <p>
            Please give us feedback in the <strong>#dashboard</strong> channel of the
            <a href="https://discord.gg/hummingbot" target="_blank">Hummingbot Discord</a>! 🙏
        </p>
        <p>
            If you encounter any bugs or have suggestions for improvement, please create an issue in the
            <a href="https://github.com/hummingbot/dashboard" target="_blank">Hummingbot Dashboard GitHub</a>.
        </p> "
        ''')


auth_system()
main()
