from fastapi import FastAPI
from pydantic import BaseModel,conlist
from typing import List,Optional
import pandas as pd
from model import calculate_meals_nutrients, calculate_nutrition, recommend,output_recommended_recipes


dataset=pd.read_csv('dataset.csv',compression='gzip')

app = FastAPI()


class params(BaseModel):
    n_neighbors:int=5
    return_distance:bool=False

class PredictionIn(BaseModel):
    metrics_input:conlist(str, min_items=4, max_items=4)   
    ingredients:list[str]=[]
    params:Optional[params]


class recommendIn(BaseModel):
    metrics_input:conlist(float, min_items=9, max_items=9)   
    ingredients:list[str]=[]
    params:Optional[params]

class Recipe(BaseModel):
    Name:str
    CookTime:str
    PrepTime:str
    TotalTime:str
    RecipeIngredientParts:list[str]
    Calories:float
    FatContent:float
    SaturatedFatContent:float
    CholesterolContent:float
    SodiumContent:float
    CarbohydrateContent:float
    FiberContent:float
    SugarContent:float
    ProteinContent:float
    RecipeInstructions:list[str]

class PredictionOut(BaseModel):
    output: Optional[dict] = None
class CustomOut(BaseModel):
    output: Optional [list[Recipe]] = None

@app.get("/")
def home():
    return {"health_check": "OK"}


@app.post("/predict/",response_model=PredictionOut)
def update_item(prediction_input:PredictionIn):
    nutrition = calculate_nutrition(prediction_input.metrics_input[0],prediction_input.metrics_input[1],prediction_input.metrics_input[2],prediction_input.metrics_input[3])
    input=calculate_meals_nutrients(nutrition)
    values_list_1 = list(input[0].values())
    values_list_2 = list(input[1].values())
    values_list_3 = list(input[2].values())

    recommendation_dataframe_1=recommend(dataset,values_list_1,prediction_input.ingredients,prediction_input.params.dict())
    recommendation_dataframe_2=recommend(dataset,values_list_2,prediction_input.ingredients,prediction_input.params.dict())
    recommendation_dataframe_3=recommend(dataset,values_list_3,prediction_input.ingredients,prediction_input.params.dict())

    output_1=output_recommended_recipes(recommendation_dataframe_1)
    output_2=output_recommended_recipes(recommendation_dataframe_2)
    output_3=output_recommended_recipes(recommendation_dataframe_3)
        
        
        # if output is None:
        #     return {"output":None}
        # else:
    new={"a":output_1,"b":output_2,"c":output_3}
    
    return {"output":{"breakfast":output_1,"lunch":output_2,"dinner":output_3}}



@app.post("/recommendCustomFood/",response_model=CustomOut)
def get_custom_meals(prediction_input:recommendIn):


    recommendation_dataframe=recommend(dataset,prediction_input.metrics_input,prediction_input.ingredients,prediction_input.params.dict())
   
    output=output_recommended_recipes(recommendation_dataframe)
    
        
        
    if output is None:
        return {"output":None}
    else:
    
        return {"output":output}
