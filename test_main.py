from datetime import datetime, timezone
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

#  ===========================================================================================================
# Timestamp microservice
# A request to /api/:date? with a valid date should return a JSON object with a unix key that is a Unix timestamp of the input date in milliseconds (as type Number)
# A request to /api/:date? with a valid date should return a JSON object with a utc key that is a string of the input date in the format: Thu, 01 Jan 1970 00:00:00 GMT
def test_timestamp_api_str():
  response = client.get("/timestamp/api/2016-12-25")
  response_json = response.json()
  print(response_json)
  assert response_json["unix"] == 1482624000000, 'Should be a valid unix timestamp'
  assert response_json["utc"] == 'Sun, 25 Dec 2016 00:00:00 GMT', 'Should be a valid UTC date string'
        
# A request to /api/1451001600000 should return { unix: 1451001600000, utc: "Fri, 25 Dec 2015 00:00:00 GMT" }
def test_timestamp_api_int():
  response = client.get("/timestamp/api/1451001600000")
  response_json = response.json()
  assert response_json["unix"] == 1451001600000 and response_json["utc"] == 'Fri, 25 Dec 2015 00:00:00 GMT'

# Your project can handle dates that can be successfully parsed by new Date(date_string)
def test_date_string_handibe():
  response = client.get("/timestamp/api/05 October 2011, GMT")
  response_json = response.json()
  assert response_json["unix"] == 1317772800000 and response_json["utc"] == 'Wed, 05 Oct 2011 00:00:00 GMT'
      
# If the input date string is invalid, the api returns an object having the structure { error : "Invalid Date" }
def test_invalid_date():
  response = client.get("/timestamp/api/this-is-not-a-date")
  response_json = response.json()
  assert response_json["error"].lower() == 'invalid date'
    
# An empty date parameter should return the current time in a JSON object with a unix key
# An empty date parameter should return the current time in a JSON object with a utc key
def test_now():
  response = client.get("/timestamp/api")
  response_json = response.json()
  now = datetime.now()
  now = now.replace(tzinfo=timezone.utc).timestamp() * 1000
  assert abs(response_json["unix"]-now) < 20000

  server_time = datetime.strptime(response_json["utc"], "%a, %d %b %Y %H:%M:%S GMT")
  server_time = server_time.replace(tzinfo=timezone.utc).timestamp() * 1000
  assert abs(server_time-now) < 20000

#  ===========================================================================================================
# Request header parser
# A request to /api/whoami should return a JSON object with your IP address in the ipaddress key.
# A request to /api/whoami should return a JSON object with your preferred language in the language key.
# A request to /api/whoami should return a JSON object with your software in the software key.
def test_whoami():
  client.headers["accept-language"] = "en-AU"
  response = client.get("/api/whoami")
  response_json = response.json()

  assert "ipaddress" in response_json and len(response_json["ipaddress"]) > 0
  assert "language" in response_json and len(response_json["language"]) > 0
  assert "software" in response_json and len(response_json["software"]) > 0


#  ===========================================================================================================
# url shortener
# You can POST a URL to /api/shorturl and get a JSON response with original_url and short_url properties. Here's an example: { original_url : 'https://freeCodeCamp.org', short_url : 1}
def test_post_shorturl():
  url = "http://localhost:8000"
  url_variable = round(datetime.now().replace(tzinfo=timezone.utc).timestamp() * 1000)
  full_url = f"{url}/?v={url_variable}"
  response = client.post(
    f"/api/shorturl",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data=f"url={full_url}",
  )
  assert response.ok
  if response.ok:
    response_json = response.json()
    assert "short_url" in response_json
    assert "original_url" in response_json
    short_url = response_json["short_url"]
    original_url = response_json["original_url"]
    assert short_url is not None
    assert original_url == f"{url}/?v={url_variable}"
  else:
    raise Exception(f"{response.status} {response.statusText}")

# When you visit /api/shorturl/<short_url>, you will be redirected to the original URL.
def test_get_shorturl():
  url = "http://localhost:8000"
  url_variable = round(datetime.now().replace(tzinfo=timezone.utc).timestamp() * 1000)
  full_url = f"{url}/?v={url_variable}"
  shortened_url_variable = None
  post_response = client.post(
    '/api/shorturl',
    headers = {'Content-Type': 'application/x-www-form-urlencoded'},
    data=f"url={full_url}"
  )
  if post_response.ok:
    post_response_json = post_response.json()
    assert "short_url" in post_response_json
    short_url = post_response_json["short_url"]
    shortened_url_variable = short_url
  else:
    raise Exception(f"{post_response.status_code} {post_response.text}")
  print(f"/api/shorturl/{shortened_url_variable}")
  get_response = client.get(f"/api/shorturl/{shortened_url_variable}")
  
  if get_response:
    assert get_response.url is not None
    url = get_response.url
    assert url == full_url
  else:
    raise Exception(f"{get_response.status_code} {get_response.text}")

# If you pass an invalid URL that doesn't follow the valid http://www.example.com format, the JSON response will contain { error: 'invalid url' }
def test_url_validation():
  response = client.post(
    "/api/shorturl",
    headers = {'Content-Type': 'application/x-www-form-urlencoded'},
    data= "url=ftp:/john-doe.invalidTLD"
  )
  if response.ok:
    response_json = response.json()
    assert "error" in response_json
    error = response_json["error"]
    assert error is not None
    assert error.lower() == 'invalid url'
  else:
    raise Exception(f"{response.status_code} {response.text}")
  

#  ===========================================================================================================
# exercise tracker
# You can POST to /api/users with form data username to create a new user.
def test_post_users():
  response = client.post(
    "/api/users",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data=f"username=fcc_test_{datetime.timestamp(datetime.now())}"[:28],
  )
  assert response.ok

# The returned response from POST /api/users with form data username will be an object with username and _id properties.
def test_post_users_response():
  response = client.post(
    "/api/users",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data=f"username=fcc_test_{datetime.timestamp(datetime.now())}"[:28],
  )
  if response.ok:
    response_json = response.json()
    assert "_id" in response_json
    assert "username" in response_json
  else:
    raise Exception(f"{response.status_code} {response.text}")

# You can make a GET request to /api/users to get a list of all users.
def test_get_users():
  response = client.get("/api/users")
  assert response.ok
    
# The GET request to /api/users returns an array.
def test_get_users_response_is_list():
  response = client.get("/api/users")
  if response.ok:
    users = response.json()
    assert isinstance(users, list)
  else:
    raise Exception(f"{response.status_code} {response.text}")

# Each element in the array returned from GET /api/users is an object literal containing a user's username and _id.
def test_get_users_response():
  response = client.get("/api/users")
  if response.ok:
    users = response.json()
    assert len(users) > 0
    user = users[0]
    assert "username" in user
    assert "_id" in user
    assert isinstance(user["username"], str)
    assert isinstance(user["_id"], str)
  else:
    raise Exception(f"{response.status_code} {response.text}")

# You can POST to /api/users/:_id/exercises with form data description, duration, and optionally date. If no date is supplied, the current date will be used.
def test_users_id_exercises():
  response = client.post(
    "/api/users",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data=f"username=fcc_test_{datetime.timestamp(datetime.now())}"[:28],
  )
  if response.ok:
    response_json = response.json()
    username = response_json["username"]
    _id = response_json["_id"]
    expected = {
      "username": username,
      "description": 'test',
      "duration": 60,
      "_id": str(_id),
      "date": 'Mon Jan 01 1990'
    }
  
    add_response = client.post(
      f"/api/users/{_id}/exercises",
      headers={"Content-Type": "application/x-www-form-urlencoded"},
      data=f"description={expected['description']}&duration={expected['duration']}&date=1990-01-01",
    )
    assert add_response.ok
    if not add_response.ok:
      raise Exception(f"{add_response.status_code} {add_response.text}")
  else:
    raise Exception(f"{response.status_code} {response.text}")

# The response returned from POST /api/users/:_id/exercises will be the user object with the exercise fields added.
def test_users_id_exercises_response():
  response = client.post(
      "/api/users",
      headers={"Content-Type": "application/x-www-form-urlencoded"},
      data=f"username=fcc_test_{datetime.timestamp(datetime.now())}"[:28],
  )
  if response.ok:
    response_json = response.json()
    username = response_json["username"]
    _id = response_json["_id"]
    expected = {
      "username": username,
      "description": 'test',
      "duration": 60,
      "_id": str(_id),
      "date": 'Mon Jan 01 1990'
    }
  
    add_response = client.post(
      f"/api/users/{_id}/exercises",
      headers={"Content-Type": "application/x-www-form-urlencoded"},
      data=f"description={expected['description']}&duration={expected['duration']}&date=1990-01-01",
    )
    if add_response.ok:
      actual = add_response.json()
      assert actual == expected
      assert isinstance(actual["description"], str)
      assert isinstance(actual["duration"], int)
      assert isinstance(actual["date"], str)
    else:
      raise Exception(f"{add_response.status_code} {add_response.text}")
  else:
    raise Exception(f"{response.status_code} {response.text}")

# You can make a GET request to /api/users/:_id/logs to retrieve a full exercise log of any user.
def test_users_id_logs():
  response = client.post(
    "/api/users",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data=f"username=fcc_test_{datetime.timestamp(datetime.now())}"[:28],
  )
  if response.ok:
    response_json = response.json()
    username = response_json["username"]
    _id = response_json["_id"]
    expected = {
      "username": username,
      "description": 'test',
      "duration": 60,
      "_id": str(_id),
      "date": str(datetime.now())
    }
  
    add_response = client.post(
      f"/api/users/{_id}/exercises",
      headers={"Content-Type": "application/x-www-form-urlencoded"},
      data=f"description={expected['description']}&duration={expected['duration']}",
    )
    if add_response.ok:
      log_response = client.get(f"/api/users/{_id}/logs")
      assert log_response.ok
      if not log_response.ok:
        raise Exception(f"{log_response.status_code} {log_response.text}")
    else:
      raise Exception(f"{add_response.status_code} {add_response.text}")
  else:
    raise Exception(f"{response.status_code} {response.text}")

# A request to a user's log GET /api/users/:_id/logs returns a user object with a count property representing the number of exercises that belong to that user.
def test_users_id_logs_count_in_response():
    response = client.post(
      "/api/users",
      headers={"Content-Type": "application/x-www-form-urlencoded"},
      data=f"username=fcc_test_{datetime.timestamp(datetime.now())}"[:28],
    )
    if response.ok:
      response_json = response.json()
      username = response_json["username"]
      _id = response_json["_id"]
      expected = {
        "username": username,
        "description": 'test',
        "duration": 60,
        "_id": str(_id),
        "date": str(datetime.now())
      }
    
      add_response = client.post(
        f"/api/users/{_id}/exercises",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f"description={expected['description']}&duration={expected['duration']}",
      )
      if add_response.ok:
        log_response = client.get(f"/api/users/{_id}/logs")
        if log_response.ok:
          log_response_json = log_response.json();
          assert "count" in log_response_json
        else:
          raise Exception(f"{log_response.status_code} {log_response.text}")
      else:
        raise Exception(f"{add_response.status_code} {add_response.text}")
    else:
      raise Exception(f"{response.status_code} {response.text}")

# A GET request to /api/users/:id/logs will return the user object with a log array of all the exercises added.
def test_users_id_logs_len():
    response = client.post(
      "/api/users",
      headers={"Content-Type": "application/x-www-form-urlencoded"},
      data=f"username=fcc_test_{datetime.timestamp(datetime.now())}"[:28],
    )
    if response.ok:
      response_json = response.json()
      username = response_json["username"]
      _id = response_json["_id"]
      expected = {
        "username": username,
        "description": 'test',
        "duration": 60,
        "_id": str(_id),
        "date": str(datetime.now())
      }
    
      add_response = client.post(
        f"/api/users/{_id}/exercises",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f"description={expected['description']}&duration={expected['duration']}",
      )
      if add_response.ok:
        log_response = client.get(f"/api/users/{_id}/logs")
        if log_response.ok:
          log_response_json = log_response.json();
          assert "log" in log_response_json
          log = log_response_json["log"]
          assert isinstance(log, list)
          assert 1 == len(log)
        else:
          raise Exception(f"{log_response.status_code} {log_response.text}")
      else:
        raise Exception(f"{add_response.status_code} {add_response.text}")
    else:
      raise Exception(f"{response.status_code} {response.text}")

# Each item in the log array that is returned from GET /api/users/:id/logs is an object that should have a description, duration, and date properties.
def test_users_id_logs_response():
    response = client.post(
      "/api/users",
      headers={"Content-Type": "application/x-www-form-urlencoded"},
      data=f"username=fcc_test_{datetime.timestamp(datetime.now())}"[:28],
    )
    if response.ok:
      response_json = response.json()
      username = response_json["username"]
      _id = response_json["_id"]
      expected = {
        "username": username,
        "description": "test",
        "duration": 60,
        "_id": str(_id),
        "date": str(datetime.now())
      }
    
      add_response = client.post(
        f"/api/users/{_id}/exercises",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f"description={expected['description']}&duration={expected['duration']}",
      )
      if add_response.ok:
        log_response = client.get(f"/api/users/{_id}/logs")
        if log_response.ok:
          log_response_json = log_response.json();
          assert "log" in log_response_json
          log = log_response_json["log"]
          assert len(log) > 0
          exercise = log[0]
          assert "description" in exercise
          assert "duration" in exercise
          assert "date" in exercise
        else:
          raise Exception(f"{log_response.status_code} {log_response.text}")
      else:
        raise Exception(f"{add_response.status_code} {add_response.text}")
    else:
      raise Exception(f"{response.status_code} {response.text}")

# The description property of any object in the log array that is returned from GET /api/users/:id/logs should be a string.
def test_users_id_logs_description_is_string():
    response = client.post(
      "/api/users",
      headers={"Content-Type": "application/x-www-form-urlencoded"},
      data=f"username=fcc_test_{datetime.timestamp(datetime.now())}"[:28],
    )
    if response.ok:
      response_json = response.json()
      username = response_json["username"]
      _id = response_json["_id"]
      expected = {
        "username": username,
        "description": 'test',
        "duration": 60,
        "_id": str(_id),
        "date": str(datetime.now())
      }
    
      add_response = client.post(
        f"/api/users/{_id}/exercises",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f"description={expected['description']}&duration={expected['duration']}",
      )
      if add_response.ok:
        log_response = client.get(f"/api/users/{_id}/logs")
        if log_response.ok:
          log_response_json = log_response.json();
          assert "log" in log_response_json
          log = log_response_json["log"]
          assert len(log) > 0
          exercise = log[0]
          assert isinstance(exercise["description"], str)
          assert exercise["description"] == expected["description"]
        else:
          raise Exception(f"{log_response.status_code} {log_response.text}")
      else:
        raise Exception(f"{add_response.status_code} {add_response.text}")
    else:
      raise Exception(f"{response.status_code} {response.text}")

# The duration property of any object in the log array that is returned from GET /api/users/:id/logs should be a number.
def test_users_id_logs_duration_is_integer():
    response = client.post(
      "/api/users",
      headers={"Content-Type": "application/x-www-form-urlencoded"},
      data=f"username=fcc_test_{datetime.timestamp(datetime.now())}"[:28],
    )
    if response.ok:
      response_json = response.json()
      username = response_json["username"]
      _id = response_json["_id"]
      expected = {
        "username": username,
        "description": 'test',
        "duration": 60,
        "_id": str(_id),
        "date": str(datetime.now())
      }
    
      add_response = client.post(
        f"/api/users/{_id}/exercises",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f"description={expected['description']}&duration={expected['duration']}",
      )
      if add_response.ok:
        log_response = client.get(f"/api/users/{_id}/logs")
        if log_response.ok:
          log_response_json = log_response.json();
          assert "log" in log_response_json
          log = log_response_json["log"]
          assert len(log) > 0
          exercise = log[0]
          assert isinstance(exercise["duration"], int)
          assert exercise["duration"] == expected["duration"]
        else:
          raise Exception(f"{log_response.status_code} {log_response.text}")
      else:
        raise Exception(f"{add_response.status_code} {add_response.text}")
    else:
      raise Exception(f"{response.status_code} {response.text}")

# The date property of any object in the log array that is returned from GET /api/users/:id/logs should be a string. Use the dateString format of the Date API.
def test_users_id_logs_date_is_string():
    response = client.post(
      "/api/users",
      headers={"Content-Type": "application/x-www-form-urlencoded"},
      data=f"username=fcc_test_{datetime.timestamp(datetime.now())}"[:28],
    )
    if response.ok:
      response_json = response.json()
      username = response_json["username"]
      _id = response_json["_id"]
      expected = {
        "username": username,
        "description": 'test',
        "duration": 60,
        "_id": str(_id),
        "date": datetime.now().strftime("%a %b %d %Y")
      }
    
      add_response = client.post(
        f"/api/users/{_id}/exercises",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f"description={expected['description']}&duration={expected['duration']}",
      )
      if add_response.ok:
        log_response = client.get(f"/api/users/{_id}/logs")
        if log_response.ok:
          log_response_json = log_response.json();
          assert "log" in log_response_json
          log = log_response_json["log"]
          assert len(log) > 0
          exercise = log[0]
          assert isinstance(exercise["date"], str)
          assert exercise["date"] == expected["date"]
        else:
          raise Exception(f"{log_response.status_code} {log_response.text}")
      else:
        raise Exception(f"{add_response.status_code} {add_response.text}")
    else:
      raise Exception(f"{response.status_code} {response.text}")

# You can add from, to and limit parameters to a GET /api/users/:_id/logs request to retrieve part of the log of any user. from and to are dates in yyyy-mm-dd format. limit is an integer of how many logs to send back.
def test_users_id_logs_limit():
    response = client.post(
        "/api/users",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f"username=fcc_test_{datetime.timestamp(datetime.now())}"[:28],
    )
    if response.ok:
      response_json = response.json()
      username = response_json["username"]
      _id = response_json["_id"]
      expected = {
        "username": username,
        "description": 'test',
        "duration": 60,
        "_id": str(_id),
        "date": str(datetime.now())
      }
      add_exercise_response = client.post(
        f"/api/users/{_id}/exercises",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f"description={expected['description']}&duration={expected['duration']}&date=1990-01-01",
      )

      add_exercise_two_response = client.post(
        f"/api/users/{_id}/exercises",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f"description={expected['description']}&duration={expected['duration']}&date=1990-01-01",
      )
      if add_exercise_response.ok and add_exercise_two_response.ok:
        log_response = client.get(f"/api/users/{_id}/logs?from=1989-12-31&to=1990-01-04")
        if log_response.ok:
          log_response_json = log_response.json();
          assert "log" in log_response_json
          log = log_response_json["log"]
          assert isinstance(log, list)
          assert 2 == len(log)
        else:
          raise Exception(f"{log_response.status_code} {log_response.text}")

        limit_response = client.get(f"/api/users/{_id}/logs?limit=1")
        if limit_response.ok:
          limit_response_json = limit_response.json();
          assert "log" in limit_response_json
          log = limit_response_json["log"]
          assert isinstance(log, list)
          assert 1 == len(log)
        else:
          raise Exception(f"{limit_response.status_code} {limit_response.text}")
        
        filter_date_before_limit_response = client.get(f"/api/users/{_id}/logs?from=1990-01-02&to=1990-01-04&limit=1")
        if filter_date_before_limit_response.ok:
          filter_date_before_limit_response_json = filter_date_before_limit_response.json();
          assert "log" in filter_date_before_limit_response_json
          log = filter_date_before_limit_response_json["log"]
          assert isinstance(log, list)
          assert 1 == len(log)
        else:
          raise Exception(f"{filter_date_before_limit_response.status_code} {filter_date_before_limit_response.text}")
      else:
        raise Exception(f"{response.status_code} {response.text}")
    else:
      raise Exception(f"{response.status_code} {response.text}")
