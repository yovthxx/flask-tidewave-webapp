class Config:
    SECRET_KEY = '04dc2a8b2d619fe40bf86ec02cdc51df' # May be changed to anything, storing SECRET_KEY as an environment variable is recommended.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tidewave.db' # Application runs on local SQLite DB but is set and tested to use something more productive, like Postgres.
    MSEARCH_INDEX_NAME = 'msearch' # This a search config, find out more at msearch project page.
    SESSION_COOKIE_HTTPONLY=True # Simple session cookie settings.
    SESSION_COOKIE_SAMESITE='Lax' # Simple session cookie settings.

    WTF_CSRF_ENABLED = False # CSRF protection is disabled to ease unit testing. Do not forget to enable CSRF protection for your WTForms if you ever plan to deploy this project.
