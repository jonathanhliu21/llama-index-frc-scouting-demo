# FRC Picklist Helper

This application uses [LlamaIndex](https://llamaindex.ai) to interpret robot scouting data in a CSV file, allowing users to analyze the performance of a certain robot using the power of ChatGPT. The analysis is then saved as a LlamaIndex document, which can be used to compare the performance of two teams or to generate a picklist.

## Usage

This app is built with streamlit. To run the app, first clone the repository, then run:

```
$ streamlit run app.py
```

A website should open showing the UI. First, upload a CSV file that contains scouting data. Make sure this file contains the column "team number" (all lowercase), as this is used to determine the team numbers. Additionally, I recommend deleting empty rows and deleting scouter name columns, as ChatGPT could mistake scouter names for robot teams.

After pressing the upload button, paste in your OpenAI key.

Before generating any comparisons or picklists, you need to generate analyses of robots. To do this, go to the Analysis tab, select a team from a dropdown, and press the Analyze button. After generating the analysis, press "Save Response"

After generating at least 2 analyses, you will able to make comparisons and picklists. In the Picklists tab, you can specify what qualities you are looking for and what you are not considering when making a picklist. If empty, then the app creates a picklist based on general qualities, such as accuracy, dead time, shot flexibility, and defense.

Under the "Saved Responses" tab, you can view generated analyses of robots. You can also save these analyses to disk. To load from disk, press the "Load Analysis History" after uploading the same file.