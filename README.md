# FIRST Robotics Competition Picklist Helper

This application uses [LlamaIndex](https://llamaindex.ai) to interpret robot scouting data in a CSV file, allowing users to analyze the performance of a certain robot using the power of ChatGPT. The analysis is then saved as a LlamaIndex document, which can be used to compare the performance of two teams or to generate a picklist.

Note that the regional competitions and team numbers shown in this demo and in the examples folder are obfuscated.

![Screenshot 2024-07-10 at 11 09 35 AM](https://github.com/jonathanhliu21/llama-index-frc-scouting-demo/assets/81734282/a2ff7a3b-8f33-47a0-8801-389f7f1e3de4)

## Context

FIRST Robotics Competition (FRC) is a high school robotics competition. Teams have six weeks to build a robot and have the opportunity to compete at regional or district events. In each event, robots compete in qualification matches, where teams of 3 are randomly chosen to compete against each other. Following the qual matches, each of the top teams pick two other teams to compete in the playoff tournament together in an alliance to win the competition. Because of this, it is important for teams to know the performance of other robots so they can make informed decisions when selecting a team.

More info on FRC can be found [here](https://www.firstinspires.org/sites/default/files/uploads/resource_library/first-robotics-competition-overview.pdf).

During qualification matches, those who are not on the drive team or pit crew (i.e. those who are not actively operating the robot) usually scout, or observe, the robots on the field. They answer questions about how each robot performs on the field, such as how many points they score or how good their driver is. These questions can be saved in a spreadsheet and exported to CSV. Below is a screenshot of a sample scouting form for the 2024 FRC game *CRESCENDO<sup>SM</sup>* presented by Haas.

![IMG_5429 Medium](https://github.com/jonathanhliu21/llama-index-frc-scouting-demo/assets/81734282/ca27f169-f8ab-4cbf-b7bc-8977e4b9431f)

This web app is useful in speeding up the process for analyzing the performance of a certain team using the power of LLMs and RAG over scouting observation CSV files. The LLM can also assist with creating a picklist, a ranking of teams to pick for an alliance during the playoffs.

Users should treat this application as an assistant and should not fully rely on it when creating a picklist or analyzing a robot, as the LLM could hallucinate or may not have the full context of a team (e.g. their reputation from previous years).

## Usage

This app is built with streamlit. To run the app, first clone the repository, then run:

```
$ streamlit run app.py
```

A website should open showing the UI. First, upload a CSV file that contains scouting data. Make sure this file contains the column "team number" (all lowercase), as this is used to determine the team numbers. Additionally, I recommend deleting empty rows and deleting scouter name columns, as ChatGPT could mistake scouter names for robot teams.

After pressing the upload button, paste in your OpenAI key.

Before generating any comparisons or picklists, you need to generate analyses of robots. To do this, go to the Analysis tab, select a team from a dropdown, and press the Analyze button. After generating the analysis, press "Save Response."

![Screenshot 2024-07-10 at 11 11 39 AM](https://github.com/jonathanhliu21/llama-index-frc-scouting-demo/assets/81734282/139f4b57-75ac-48bd-8d73-d28845e4ccbe)

After generating at least 2 analyses, you will able to make comparisons and picklists. In the Picklists tab, you can specify what qualities you are looking for and what you are not considering when making a picklist. If empty, then the app creates a picklist based on general qualities, such as accuracy, dead time, shot flexibility, and defense.

![Screenshot 2024-07-10 at 11 31 58 AM](https://github.com/jonathanhliu21/llama-index-frc-scouting-demo/assets/81734282/50f0f742-91b2-45c5-b39c-cc82968d0294)

Under the "Saved Responses" tab, you can view generated analyses of robots. You can also save these analyses to disk. To load from disk, press the "Load Analysis History" after uploading the same file.

![Screenshot 2024-07-10 at 11 34 53 AM](https://github.com/jonathanhliu21/llama-index-frc-scouting-demo/assets/81734282/f51e7089-2ef5-4da5-b217-95c9ce87624b)
