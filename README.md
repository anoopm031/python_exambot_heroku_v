# python_exambot_heroku_v
This is the publicised repository of @exam_edu_bot in telegram hosted in Heroku with a Postgresql database. 
During COVID and lockdown any teacher who wants to engage thier students through assignments and tests can do it easily through this bot. 
- `test_gen.py` is the main file. I didn't split `test_gen` into smaller components to avoid passing bot object each time a function is called, which is very frequent.

- store.py contains pycopg2-postgres databse codes. `classes.py` contains test class and `user_class.py` contains other used classes.

- https://t.me/Exam_edu_bot?start   - to checkout the bot

- Test creation example video: https://youtu.be/RAUyG97eNis

- Test attempting example video: https://youtu.be/U-ZEEzZlRVQ

- I might be adding a subjective test availability with the help of AWS S3 buckets.
