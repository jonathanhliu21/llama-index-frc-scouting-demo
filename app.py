import csv
import os
from pathlib import Path
import typing as t

from llama_index.core import (
    StorageContext,
    load_index_from_storage,
    SummaryIndex,
    Settings,
)
from llama_index.core.schema import Document
from llama_index.llms.openai import OpenAI
import numpy as np
import pandas as pd
import streamlit as st


CSV_READER_PROMPT_STR = """
You are asked to analyze the performance of a certain robot.

First, check whether a robot exists. If a robot does not exist, do not analyze.

Second, consider the categories below:
1. Autonomous performance: How many amp/speaker shots can each robot make, and how reliable is it?
    How often does the robot leave the starting zone? How often did the robot access the notes in the middle of the field?
2. Speaker performance: How consistently is the robot able to shoot into the speaker with low cycle times?
    How flexible was the robot with shooting from certain locations?
3. Amp performance: How consistently is the robot able to shoot into the amp with low cycle times?
4. Dead time: How much time was the robot dead or broken?
5. Endgame: How reliably does a robot park? How reliably does a robot climb? Distinguish between parking and climbing.
6. Trap: How often does the robot trap?
7. Type of robot: How often did the robot play offense or defense? Did the robot mostly shoot into speaker or amp?
8. Defense: How often did the robot play defense?
9. Additional Comments: What additional information do the comments reveal?

Do not draw conclusions or make assumptions from this data. Make sure data comes from the correct column.

Summarize your response in a series of markdown bullet points, no headings. Don't include "team x has a robot."
"""

PICKLIST_STR = """
Create a single picklist of robots. Make sure to include ALL robots in the context.

General criteria for higher-ranking robots:
- Able to exit their starting area during autonomous
- High scoring (in either the amp and the speaker) during the autonomous period, with good accuracy
- If they are a speaker robot, then they have good accuracy when shooting into the speaker during the teleoperated period and ideally high-scoring too.
- If they are an amp robot, then they have good accuracy when shooting into the amp during the teleoperated period and ideally high-scoring too.
- If they are a defense robot, then they have a high percentage of time on defense.
- They are never dead or broken, or only die in one or two very early matches in the competition.
- They are flexible with where they are able to shoot from.

You do not have to be rigid with these criteria, as the user will be more specific with what criteria
    they want when picking a robot.
"""


def load_data(
    file: Path, extra_info: t.Optional[t.Dict] = None, team_no: str = None
) -> t.List[Document]:
    """Custom load data for CSV - includes team number in metadata

    Args:
        file (Path): File path
        extra_info (t.Optional[t.Dict], optional): Other metadata. Defaults to None.
        team_no (str, optional): Team number. Defaults to None.

    Returns:
        t.List[Document]: List of documents
    """

    text_list = []
    with open(file) as fp:
        csv_reader = csv.reader(fp)

        headings = next(csv_reader)
        text_list.append(
            {
                "text": ",".join(headings),
            }
        )

        for row in csv_reader:
            team_number = row[1]  # under the team number column
            if not team_no or str(team_number) == team_no:
                text_list.append(
                    {"text": ", ".join(row), "team_number": str(team_number)}
                )

    metadata = {"filename": file.name, "extension": file.suffix}
    if extra_info:
        metadata = {**metadata, **extra_info}

    res = [Document(text=text_list[0]["text"], metadata=metadata)]

    return res + [
        Document(
            text=el["text"],
            metadata={**metadata, "team_number": el["team_number"]},
        )
        for el in text_list[1:]
    ]


if "file_name" not in st.session_state:
    st.session_state["file_name"] = None
if "saved_dict" not in st.session_state:
    st.session_state["saved_dict"] = {}
if "cur_response" not in st.session_state:
    st.session_state["cur_response"] = ""
if "cur_team" not in st.session_state:
    st.session_state["cur_team"] = ""
if "csv_docs" not in st.session_state:
    st.session_state["csv_docs"] = ""
if "lf" not in st.session_state:
    st.session_state["lf"] = ""
if "nlf" not in st.session_state:
    st.session_state["nlf"] = ""

# title page and upload widget
st.set_page_config(page_title="FRC Picklist Helper", page_icon=":robot_face:")
st.title("FRC Picklist Helper")
upload = st.file_uploader("Upload a CSV File representing scouting data spreadsheet")


def initialize_CSV_docs(fname):
    """Returns CSV index"""
    Settings.llm = OpenAI(temperature=0, model="gpt-4o")

    csv_docs = load_data(
        file=Path("data") / Path(fname),
        extra_info={"name": "FRC Competition Robot Observation Data"},
    )
    return csv_docs


def filter_docs(docs: t.List[Document], team_no: str) -> t.List[Document]:
    """Only returns documents that contain section headings and team number"""
    return [
        doc
        for doc in docs
        if "team_number" not in doc.metadata or doc.metadata["team_number"] == team_no
    ]


def save_callback(team_no, response):
    """Saves response of team number to session state"""

    st.session_state["saved_dict"][team_no] = str(response)
    st.success("Successfully saved response")


def clear_callback():
    """Clears current response on analysis page"""

    st.session_state["cur_response"] = ""
    st.session_state["cur_team"] = ""


# upload widget
if st.button("Upload file"):
    if upload is None:
        st.error("Upload a file first")
    else:
        data = upload.getvalue().decode("utf-8")

        fpath = os.path.join("data", upload.name)
        with open(fpath, "w") as f:
            f.write(data)

        # saves file info to session state
        st.success("Succesfully uploaded file")
        st.session_state["file_name"] = upload.name
        st.session_state["cur_team"] = ""
        st.session_state["cur_response"] = ""
        st.session_state["saved_dict"] = {}
        st.session_state["cur_df"] = None

        with st.spinner("Initializing..."):
            st.session_state["csv_docs"] = initialize_CSV_docs(
                st.session_state["file_name"]
            )


# loads previous analyses if saved
if (
    "file_name" in st.session_state
    and st.session_state["file_name"]
    and os.path.exists("storage_{}".format(st.session_state["file_name"]))
):
    if st.button("Load Analysis History"):
        ctx = StorageContext.from_defaults(
            persist_dir="storage_{}".format(st.session_state["file_name"])
        )
        index = load_index_from_storage(ctx)

        # gets raw text from docstore
        for doc_id in index.docstore.get_all_document_hashes().values():
            doc = index.docstore.get_document(doc_id)
            team_no = str(doc.metadata["team_no"])
            text = doc.get_text()

            st.session_state["saved_dict"][team_no] = str(text)

        st.success("Successfully Loaded Text History")


# load CSV into pandas
if st.session_state["file_name"] is not None and st.session_state["cur_df"] is None:
    st.session_state["cur_df"] = pd.read_csv(
        os.path.join("data", st.session_state["file_name"])
    )

# gets OpenAI API key
api_key = st.text_input("Enter your OpenAI API key here", type="password")
os.environ["OPENAI_API_KEY"] = api_key

# tabs
analysis_tab, compare_tab, picklists, saved_responses = st.tabs(
    ["Analysis", "Comparisons", "Picklists", "Saved Responses"]
)


# analysis
with analysis_tab:
    if st.session_state["file_name"] is None:
        st.markdown("Please upload a file first")
    else:
        team_no = str(
            st.selectbox(
                "Choose one of the following teams to analyze",
                np.sort(st.session_state["cur_df"]["team number"].unique()),
            )
        )

        if st.button("Analyze"):
            if "csv_docs" in st.session_state and st.session_state["csv_docs"]:
                # filters documents to match team number, then querys these docs using a SummaryIndex
                filtered_docs = filter_docs(st.session_state["csv_docs"], team_no)
                index = SummaryIndex.from_documents(filtered_docs)
                chat_eng = index.as_chat_engine(
                    similarity_top_k=10, system_prompt=CSV_READER_PROMPT_STR
                )
                prompt = (
                    f"Please analyze the performance of team {team_no}. Only focus on this team, make sure team_no metadata matches."
                    'Do not use data from other teams. Do not say obvious statements like "Team x has a robot."'
                )

                with st.spinner("Analyzing (this may take a while)..."):
                    st.session_state["cur_response"] = chat_eng.chat(prompt)
                    st.session_state["cur_team"] = str(team_no)
            else:
                st.markdown("Please initialize the index")

        # prints response
        if st.session_state["cur_response"] and st.session_state["cur_team"]:
            st.markdown(st.session_state["cur_response"])

            st.button(
                "Save Response",
                on_click=save_callback,
                args=(st.session_state["cur_team"], st.session_state["cur_response"]),
            )

            st.button("Clear", on_click=clear_callback)

# comparisons
with compare_tab:
    if st.session_state["file_name"] is None:
        st.markdown("Please upload a file first")
    else:
        # loads text of previous analyses and puts them into documents
        docs = [
            Document(text=text, metadata={"team_no": team_no})
            for team_no, text in st.session_state["saved_dict"].items()
        ]

        if len(docs) < 2:
            st.markdown("Please generate analyses of at least 2 teams first.")
        else:
            # displays team menus
            col1, col2 = st.columns([1, 1])

            with col1:
                team_nos = np.sort(
                    np.array(
                        [int(team_no) for team_no in st.session_state["saved_dict"]]
                    )
                )
                team_no_1 = st.selectbox(
                    "Choose one of the following teams to compare",
                    team_nos,
                )

            with col2:
                idx = np.argwhere(team_nos == team_no_1)
                team_nos_cpy = np.delete(team_nos, idx)
                team_no_2 = st.selectbox("Choose another team to compare", team_nos_cpy)

            if st.button("Compare"):
                # using previous analyses, loads into index and displays response
                index = SummaryIndex.from_documents(docs)
                chat_eng = index.as_chat_engine()
                prompt = (
                    f"Please compare the performance of team {team_no_1} to team {team_no_2}."
                    "Only focus on these teams. Do not use data from other teams."
                    "Make a recommendation on which team you would pick over the other."
                )

                with st.spinner("Comparing (this may take a while)..."):
                    response = chat_eng.chat(prompt)

                st.markdown(response)

# picklists
with picklists:
    if st.session_state["file_name"] is None:
        st.markdown("Please upload a file first")
    else:
        st.markdown(
            "Creates a picklist based on the saved analyses generated in the Analysis tab."
        )

        # loads previously saved analyses and puts into summaryindex
        docs = [
            Document(text=text, metadata={"team_no": team_no})
            for team_no, text in st.session_state["saved_dict"].items()
        ]
        index = SummaryIndex.from_documents(docs)

        if len(docs) < 2:
            st.markdown("Please generate analyses of at least 2 teams first.")
        else:
            # prints current teams
            cur_teams = ", ".join(
                sorted(
                    [team_no for team_no in st.session_state["saved_dict"]],
                    key=lambda x: int(x),
                )
            )
            st.markdown("Current generated teams: " + cur_teams)

            # gets what to consider and not to consider when picking teams
            st.session_state["lf"] = st.text_area(
                "Categories you're looking for (e.g. defense, amp, speaker):",
                value=st.session_state["lf"],
            )
            st.session_state["nlf"] = st.text_area(
                "Categories you're not looking for:", value=st.session_state["nlf"]
            )

            # gets response
            if st.button("Generate Picklist"):
                with st.spinner("Generating picklist (may take a while)..."):
                    eng = index.as_chat_engine(system_prompt=PICKLIST_STR)

                    lf = ""
                    nlf = ""
                    if st.session_state["lf"].strip():
                        lf = "{} is important.".format(st.session_state["lf"].strip())
                    if st.session_state["nlf"].strip():
                        nlf = "{} is not important.".format(
                            st.session_state["nlf"].strip()
                        )

                    response = eng.chat(
                        f"These are the current teams {cur_teams}. Based on the context, create a picklist of teams, best to worst."
                        f"{lf} {nlf} Make sure to include all teams."
                    )

                st.markdown(response)

# view previous responses
with saved_responses:
    if st.session_state["file_name"] is None:
        st.markdown("Please upload a file first")
    elif not st.session_state["saved_dict"]:
        st.markdown("Please save an analysis first")
    else:
        # saves to disk
        if len(docs) > 0:
            if st.button("Save analyses to disk"):
                with st.spinner("Saving..."):
                    index = SummaryIndex.from_documents(docs)
                    fname = st.session_state["file_name"]
                    index.storage_context.persist(persist_dir=f"storage_{fname}")

                st.success("Saved analyses to disk")

        team_no = st.selectbox(
            "Choose one of the following teams to view",
            sorted(st.session_state["saved_dict"].keys(), key=lambda x: int(x)),
        )

        if st.button("View Analysis"):
            st.markdown(st.session_state["saved_dict"][team_no])
