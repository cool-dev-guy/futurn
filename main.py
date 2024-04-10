from playwright.async_api import async_playwright
from solver import solver
from fastapi import FastAPI,Request

app = FastAPI()


@app.get("/")
async def root():
    return {
        "Status": 200,
        "Data":{}
    }


@app.post("/turnstile/{id:str}")
async def read_item(id:str,request:Request):
    try:
        body = await request.json()
        sitekey:str = id
        url:str = body['url']
        invisible:bool = body['invisible']
        print(url,sitekey)
        if not url and not sitekey:
            return {
                "Status": 500,
                "Data":{}
            }
        else:
            async with async_playwright() as playwright:
                cool_solver = solver.Solver(playwright, headless=True)
                captcha = await cool_solver.solve(url,sitekey, invisible=invisible)
                await cool_solver.terminate()
                return {
                    "Status": 200,
                    "Data":{
                            "key":captcha                
                        }
                    }
    except Exception as e:
        return {
            "Status": 500,
            "Data": {"error": str(e)}
        }
