# App: Interactive Analysis for "A Deep Reinforcement Learning Aided Inventory Control Approach 
for Managing Drug Shortages"

## Overview
A Streamlit app for analysis the results of multi-agent DRL-based inventory management problem

Additional info is shown on the FAQ page of the app itself.

### App logic
```
|--- Home.py                         <- main file that runs the app
|--- metrics.py                      <- 
|--- pages                           <- folder for additional app pages
    |--- 2_bulb_FAQ.py                  <- FAQ page
|--- app_data                        <- not in this repo

```

#### Home:
1) Show welcome section


#### FAQ:
1) Explain key metrics
2) Explain data



## Run
### Locally
1) Git clone this repo
2) Add `app_data` folder with data files 
3) Open terminal and move to folder containing `Home.py`
4) Type `streamlit run Home.py` in your terminal


## Deploy
Deploy like any other Streamlit application, for instance, on a virtual machine in a virtual environment within a `screen` session, using an open port (see [Deploy Streamlit App](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app) for more info).
