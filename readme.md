<h1>LangGraph Tutorial</h1>

<h2>Watch the full tutorial on my YouTube Channel</h2>
<div>

<a href="">
    <img src="thumbnail_small.png" alt="Thomas Janssen Youtube" width="200"/>
</a>
</div>

<h2>Prerequisites</h2>
<ul>
  <li>Python 3.11+</li>
</ul>

<h2>Installation</h2>
<h3>1. Clone the repository:</h3>

```
git clone https://github.com/ThomasJanssen-tech/LangGraph_Tutorial
cd LangGraph_Tutorial
```

<h3>2. Create a virtual environment</h3>

```
python -m venv venv
```

<h3>3. Activate the virtual environment</h3>

```
venv\Scripts\Activate
(or on Mac): source venv/bin/activate
```

<h3>4. Install libraries</h3>

```
pip install -r requirements.txt
```

<h3>5. Configuration</h3>
<ul>
<li>Rename the .env.example file to .env</li>
<li>Get your free Bright Data API Key: https://brdta.com/tomstechacademy</li>
<li>Add your Bright Data API key to the .env file</li>
</ul>

<h2>Executing the scripts</h2>

- Open a terminal in VS Code

- Execute the following commands:

```
python 1_langgraph_simple_example.py
streamlit run 2_langgraph_chatbot.py
streamlit run 3_langgraph_research_agent.py
```
