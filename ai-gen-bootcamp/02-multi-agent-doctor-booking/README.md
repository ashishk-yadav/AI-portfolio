```
conda create -p venv python=3.12 -y
```

```
conda activate /Users/preetyrai/DoctorAppointment/venv

```

```
pip install -r requirements.txt 

```

```shell
python setup.py develop
```


```

uvicorn main:app --reload --port 8002 


streamlit run streamlit_ui.py 

``` 




```

Doctor Appointment System using LangGraph, FastAPI, Streamlit 

This project is a multi-agent, AI-powered Doctor Appointment Booking System that simulates a realistic medical assistant capable of handling user queries regarding doctor availability, specialization, and appointment booking. 


```

``` 
Tech Stack: 

1. Langgraph for workflow automation between agents 

2. Langchain for Model Loading, Prompt Creation and tool usage 

3. FastAPI for serving the API endpoint/execute 

4. Streamlit for frontend interaction 

5. Python + Pandas + CSV for data handling 

```




