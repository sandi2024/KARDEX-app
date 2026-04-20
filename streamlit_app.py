import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime 
def main():
    
    st.set_page_config(
        page_title="ANALSIS DE DATOS: KARDEX",
        layout="wide",
        initial_sidebar_state="expanded"
    )
   
    st.title("Kardex")
    st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
    )


if __name__ == '__main__':
    main()
