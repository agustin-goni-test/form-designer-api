# main.py
from fastapi import FastAPI, HTTPException
from routers import test_api, form_definition_api,  component_definition_api 


app = FastAPI(title="Form API", version="0.1")

# Register routers
app.include_router(test_api.router)
app.include_router(form_definition_api.router)
app.include_router(component_definition_api.router)

