
def new_user_extract(params):
  from datetime import datetime

  return {
    'timestamp': datetime.strptime(params.get('timestamp'), '%m/%d/%Y %H:%M:%S'),
    'email': params.get('email'),
    'consent_accept': 'yes' == params.get('consent_appept'),
    'firstname': params.get('firstname'),
    'lastname': params.get('lastname')
  }

def access_key(email, timestamp, recieve_timestamp):
  import os, hashlib, datetime

  h = hashlib.sha256()
  accept_timestamp = int(timestamp.timestamp())
  recieve_timestamp = int(recieve_timestamp.timestamp())
  print(accept_timestamp, '---', recieve_timestamp)

  h.update(f'{accept_timestamp}.{recieve_timestamp}-{email}@{os.getenv("APP_SECRET_KEY")}'.encode())
  serial = h.hexdigest()[:10]

  return f"{serial[:3]}-{serial[3:6]}-{serial[-4:]}".lower()

def prepare_music_list(user):
  pass