
![Screenshot](https://github.com/udelblue/AI-Azure-Services/blob/main/images/Screenshot.png)

---
page_type: example
description: "A example app that can be used to demonstrate Azure AI Services."
languages:
- python
products:
- azure
- azure-ai
---

# Deploy a Python (FastAPI) web app to Azure App Service 

This is example app of FastAPI application for the Azure AI services. You will need to create a .env and fill in the necessary properties prior to local and azure deployment. 


## Local Testing

To try the application on your local machine:

### Install the requirements

`pip install -r requirements.txt`

### Start the application

`uvicorn main:app --reload`

### Example call

http://127.0.0.1:8000/

## Deploy to Azure infrastucture 

`azd up`

## Deploy app to Azure 

`azd deploy`