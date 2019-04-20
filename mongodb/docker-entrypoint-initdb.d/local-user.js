db = db.getSiblingDB('tiny');

db.createUser({
  'user': 'local-user',
  'pwd': 'local-user-password',
  'roles': [
    {
      'role': 'readWrite',
      'db': 'tiny'
    }
  ]
});
