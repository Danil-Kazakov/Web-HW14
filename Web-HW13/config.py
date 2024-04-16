from pydantic import BaseConfig


class Settings(BaseConfig):
    """
        Configuration settings for the application.

        Attributes:
            sqlalchemy_database_url (str): URL for the SQLAlchemy database connection.
            secret_key (str): Secret key used for encryption.
            algorithm (str): Encryption algorithm.
            mail_username (str): Username for sending emails.
            mail_password (str): Password for sending emails.
            mail_from (str): Email address from which emails are sent.
            mail_port (int): Port for the email server.
            mail_server (str): SMTP server for sending emails.
            redis_host (str): Hostname of the Redis server (default: 'localhost').
            redis_port (int): Port of the Redis server (default: 6379).
            cloudinary_name (str): Cloudinary account name.
            cloudinary_api_key (str): Cloudinary API key.
            cloudinary_api_secret (str): Cloudinary API secret.

        """
    sqlalchemy_database_url: str
    secret_key: str
    algorithm: str
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    redis_host: str = 'localhost'
    redis_port: int = 6379
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    sqlalchemy_database_url: int

    class Config:
        """
               Configuration for loading settings from an environment file.

               Attributes:
                   env_file (str): Path to the environment file.
                   env_file_encoding (str): Encoding of the environment file.
               """
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
