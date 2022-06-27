from datetime import datetime, timezone
import validators as v
from database import create_db_and_tables, engine
from helpers.timestamp import get_date_from_str, make_res
from uvicorn import run
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, Form, File, UploadFile
from sqlmodel import Session, select
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse

from models import Hero, User, Url, Exercise

from sqlmodel.sql.expression import Select, SelectOfScalar

SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get('/')
async def root():
    return {'message': 'Hello World'}

@app.get('/timestamp/api')
async def timestamp_now():
    return make_res(datetime.now())

@app.get('/timestamp/api/{date}')
async def timestamp(date: str):
    try:
        dt_obj = datetime.fromtimestamp(int(date) / 1000, timezone.utc)
        res = make_res(dt_obj)
    except:
        try:
            dt_obj: datetime = get_date_from_str(date)
            res = make_res(dt_obj)
        except:
            res = {"error" : "Invalid Date"}
    return res


@app.get('/api/whoami')
async def whoami(request: Request):
  headers = request.headers
  client = request.client
  return {
    "ipaddress": client.host,
    "language": headers["accept-language"],
    "software": headers["user-agent"],
  }


@app.get("/api/shorturl", response_class=HTMLResponse)
async def render_shorturl_page(request: Request):
  return templates.TemplateResponse("item.html", {"request": request})

@app.post('/api/shorturl')
async def post_shorturl(url: str = Form()):
  if not v.url(url):
    return {'error': 'invalid url'}
  
  with Session(engine) as session:
        urls = session.exec(select(Url)).all()
        original_urls = list(map(lambda url: url.original_url, urls))
        if url in original_urls:
          return session.get(Url, url)
        else:
          url = Url(short_url=(len(urls) + 1), original_url=url)
          session.add(url)
          session.commit()
          session.refresh(url)
          return url

@app.get('/api/shorturl/{id}')
async def get_shorturl(id: int):
  with Session(engine) as session:
    url = session.exec(select(Url).where(Url.short_url==id)).first()
    return RedirectResponse(url.original_url, status_code=303)
    
    
@app.get("/api/exercise-tracker", response_class=HTMLResponse)
async def render_exercise_tracker_page(request: Request):
  return templates.TemplateResponse("exercise-tracker.html", {"request": request})


@app.get('/api/users')
async def get_users():
  with Session(engine) as session:
    users = session.exec(select(User)).all()
    users = list(
      map(
        lambda user: {
          "username": user.username,
          "_id": str(user.id)
        },
        users
      )
    )
    return users

@app.post('/api/users')
async def post_users(username: str = Form()):
  user = User(username=username)
  with Session(engine) as session:
    session.add(user)
    session.commit()
    session.refresh(user)
    return {
      "username": user.username,
      "_id": str(user.id)
    }

@app.post('/api/users/{_id}/exercises')
async def add_exercise(
  _id: int,
  description: str = Form(),
  duration: int = Form(),
  date: str | None = Form(default=datetime.now().strftime("%Y-%m-%d"))
):
  with Session(engine) as session:
    user = session.get(User, _id)
    date_dt: datetime = datetime.strptime(date, "%Y-%m-%d")
    exercise = Exercise(
      description=description,
      duration=duration,
      date=date_dt.strftime("%a %b %d %Y"),
      user_id=_id      
    )
    session.add(exercise)
    session.commit()
    session.refresh(exercise)
    user_dict = {
      "username": user.username,
      "description": exercise.description,
      "duration": exercise.duration,
      "date": exercise.date,
      "_id": str(_id)
    }
    return user_dict

@app.get('/api/users/{_id}/logs')
async def get_logs(_id: int,  request: Request):
  query_params = request.query_params
  from_ = query_params.get("from")
  to = query_params.get("to")
  limit: int | None = query_params.get("limit")

  print(from_, to, limit)
  print(type(from_), type(to), type(limit))

  with Session(engine) as session:
    user = session.get(User, _id)
    exercises = session.exec(select(Exercise).where(
      Exercise.user_id == _id
    )).all()

    if limit is not None:
      exercises = exercises[:int(limit)]
    
    return {
      "username": user.username,
      "count": len(exercises),
      "_id": str(_id),
      "log": exercises
    }

@app.get("/fileupload", response_class=HTMLResponse)
async def get_file(request: Request):
  return templates.TemplateResponse(
    "file.html", {"request": request}
  )

@app.post("/api/fileanalyse")
async def create_upload_file(upfile: UploadFile | None = None):
  if not upfile:
    return {"message": "No upload file sent"}
  else:
    return {
      "name": upfile.filename,
      "type": upfile.content_type,
      "size": upfile.spool_max_size,
    }


@app.post("/heroes/")
def create_hero(hero: Hero):
    
    with Session(engine) as session:
        session.add(hero)
        session.commit()
        session.refresh(hero)
        return hero


@app.get("/heroes/")
def read_heroes():
    with Session(engine) as session:
        heroes = session.exec(select(Hero)).all()
        return heroes


if __name__ == '__main__':
  run("main:app", reload=True)
#   run("main:app", host="0.0.0.0", port=8000, reload=True)