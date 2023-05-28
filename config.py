import os

from dotenv import load_dotenv
from pydantic import BaseSettings

from app import constants


class BaseConfig(BaseSettings):
    # reminder: general application settings
    app_id: str = constants.APPLICATION_id
    secret_key: str = ""
    log_header: str = constants.LOG_HEADER
    # reminder: postgres database config
    db_host: str = ""
    db_user: str = ""
    db_password: str = ""
    db_name: str = ""
    db_port: str = ""
    # reminder: redis server config
    redis_server: str = ""
    redis_port: str = ""
    redis_password: str = ""
    # reminder: jwt config
    jwt_algorithms = ["HS256", "RS256"]
    jwt_public_key: str = ""
    # reminder: mail server config
    mail_server: str = ""
    mail_server_port: str = ""
    default_mail_sender_address: str = ""
    default_mail_sender_password: str = ""
    admin_mail_addresses: str = ""
    # kafka server config
    kafka_bootstrap_servers: str = ""
    kafka_server_username: str = ""
    kafka_server_password: str = ""
    kafka_subscriptions: str = ""
    kafka_consumer_group_id: str = "FASTAPI_GROUP"
    # keycloak server config
    keycloak_uri: str = ""
    keycloak_realm: str = ""

    @property
    def SQLALCHEMY_DATABASE_URI(self):  # noqa
        return "postgresql+psycopg2://{db_user}:{password}@{host}:{port}/{db_name}".format(  # noqa
            db_user=self.db_user,
            host=self.db_host,
            password=self.db_password,
            port=self.db_port,
            db_name=self.db_name,
        )

    class Config:
        env_file = ".env"


class DevelopmentConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f"sqlite:///{self.db_name}.sqlite3?check_same_thread=False"


def get_settings():
    load_dotenv(".env")
    config_cls_dict = {
        constants.DEVELOPMENT_ENVIRONMENT: DevelopmentConfig,
        constants.PRODUCTION_ENVIRONMENT: ProductionConfig,
        constants.TESTING_ENVIRONMENT: TestingConfig,
    }
    config_name = os.getenv("FASTAPI_CONFIG", default=constants.DEVELOPMENT_ENVIRONMENT)
    config_cls = config_cls_dict[config_name]
    return config_cls()


settings = get_settings()
