from datetime import datetime
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

# // You can POST to /api/users with form data username to create a new user.
def test_post_users():
  response = client.post(
    "/api/users",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data=f"username=fcc_test_{datetime.timestamp(datetime.now())}"[:28],
  )
  assert response.ok

# // The returned response from POST /api/users with form data username will be an object with username and _id properties.
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

# // You can make a GET request to /api/users to get a list of all users.
def test_get_users():
  response = client.get("/api/users")
  assert response.ok
    
# // The GET request to /api/users returns an array.
def test_get_users_response_is_list():
  response = client.get("/api/users")
  if response.ok:
    users = response.json()
    assert isinstance(users, list)
  else:
    raise Exception(f"{response.status_code} {response.text}")

# // Each element in the array returned from GET /api/users is an object literal containing a user's username and _id.
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

# // You can POST to /api/users/:_id/exercises with form data description, duration, and optionally date. If no date is supplied, the current date will be used.
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

# // The response returned from POST /api/users/:_id/exercises will be the user object with the exercise fields added.
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

# // You can make a GET request to /api/users/:_id/logs to retrieve a full exercise log of any user.
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

# // A request to a user's log GET /api/users/:_id/logs returns a user object with a count property representing the number of exercises that belong to that user.
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

# // A GET request to /api/users/:id/logs will return the user object with a log array of all the exercises added.
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

# // Each item in the log array that is returned from GET /api/users/:id/logs is an object that should have a description, duration, and date properties.
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

# // The description property of any object in the log array that is returned from GET /api/users/:id/logs should be a string.
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

# // The duration property of any object in the log array that is returned from GET /api/users/:id/logs should be a number.
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

# // The date property of any object in the log array that is returned from GET /api/users/:id/logs should be a string. Use the dateString format of the Date API.
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

# // You can add from, to and limit parameters to a GET /api/users/:_id/logs request to retrieve part of the log of any user. from and to are dates in yyyy-mm-dd format. limit is an integer of how many logs to send back.
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
