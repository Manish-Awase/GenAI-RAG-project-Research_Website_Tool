import streamlit as st
import time

from rag import process_urls
from rag import  generate_answer
from utils import validate_urls
# Store previous input in session state
if "prev_input" not in st.session_state:
    st.session_state.prev_input = ""

# Store previous url_list in session state
if "url_list" not in st.session_state:
    st.session_state.url_list = []

# Store previous url_complete_state in session state for completion of process_url function
if "url_complete_state" not in st.session_state:
    st.session_state.url_complete_state = ""

st.title('Research website through URL')

# url sidebar
st.sidebar.title('URL')
url1=st.sidebar.text_input(label="URL1",placeholder='Enter URL')
url2=st.sidebar.text_input(label="URL2",placeholder='Enter URL')
url3=st.sidebar.text_input(label="URL3",placeholder='Enter URL')
b_pressed=st.sidebar.button(label='Process URLs')
col_left, col_right = st.columns([1,3])
# Error reporting column
with col_left:
    status=st.empty()
    space=st.empty()
    space.write("&nbsp;")
    error=st.empty()
    temp=st.empty()

# main area column
with col_right:
    # input field
    input_field=st.empty()

    answer=st.empty()

# main code
# url
if not b_pressed:
    status.markdown("**Status:** ⏳ Idle")
# if Process URLs button pressed
if b_pressed:

    urls = [url for url in (url1, url2) if url.strip() != ""]
    valid_url_list=validate_urls(urls)

    # check if urls are present
    if valid_url_list:

        # check if urls are changed after submit button is pressed(means new urls are entered)
        if not (set(valid_url_list) == set(st.session_state.url_list)):
    # ////////////////////////////asking url
            status.markdown("✅ URLs processing ...")
            for i, u in enumerate(urls, 1):
                st.write(f"Valid URL {i}.: {u}")
            for state in process_urls(urls):
                st.write(f"**Status:** {state}")
        status.markdown(f"**Status:** ✅ Success: URLs processed.")
        time.sleep(1)
        st.session_state.url_complete_state="document added in vectorstore"
    else:
        st.session_state.url_complete_state = "document not added in vectorstore"
        error.markdown("enter valid url")
    st.session_state.url_list = valid_url_list
# input query

user_input =input_field.text_input(label="",placeholder="Type your question here...")


# Detect Enter press by comparing current and previous input
if user_input and user_input != st.session_state.prev_input:
    # st.write(f"Enter pressed! You typed: {user_input}")
    st.session_state.prev_input = user_input+str(time.time())
    if st.session_state.url_complete_state == "document added in vectorstore":
        status.markdown(f"**Status:** Generating answer...")
        output_text, source = generate_answer(user_input)


        source_list= [f"\n\n:{doc.metadata['source']}" for  doc in source]
        answer.markdown(f"output_text:\n {output_text}\n\n sources:{' '.join(set(source_list))}")





status.markdown("**Status:** ⏳ Idle")
