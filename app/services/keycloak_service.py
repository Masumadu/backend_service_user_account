import inspect
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import requests
from requests import Response, exceptions

from app import constants
from app.core.exceptions import AppException
from app.core.log import get_error_context, get_full_class_name
from app.core.service_interfaces import AuthServiceInterface
from config import settings

CLIENT_ID: str = settings.keycloak_client_id
CLIENT_SECRET: str = settings.keycloak_client_secret
URI: str = settings.keycloak_uri
REALM: str = settings.keycloak_realm
REALM_PREFIX: str = "/realms/"
REALM_URL: str = f"{REALM_PREFIX}{REALM}"
ADMIN_REALM_URL: str = "/admin/realms/"
AUTH_ENDPOINT: str = "/protocol/openid-connect/token/"
OPENID_CONFIGURATION_ENDPOINT: str = "/.well-known/openid-configuration"
JWT_CERTS_ENDPOINT: str = "/protocol/openid-connect/certs"
JWT_ISSUER: str = f"{URI}{REALM_PREFIX}{REALM}"


@dataclass
class KeycloakAuthService(AuthServiceInterface):
    """
    This class is an intermediary between this service and the IAM service i.e Keycloak.
    It makes authentication and authorization API calls to the IAM service on
    behalf of the application. Use this class when authenticating an entity.
    """

    roles = []

    def get_token(self, obj_data: Dict[str, str]) -> Dict[str, str]:
        """
        Login to Keycloak and return token.

        :param obj_data: A dictionary containing username and password.
        :type obj_data: dict[str, str]
        :return: A dictionary containing token and refresh token.
        :rtype: dict[str, str]
        :raises AssertionError: If request data is missing or not a dict.
        """
        assert obj_data, constants.ASSERT_NULL_OBJECT
        assert isinstance(obj_data, dict), constants.ASSERT_DICT_OBJECT

        data: Dict[str, str] = {
            "grant_type": "password",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "username": obj_data.get("username"),
            "password": obj_data.get("password"),
        }
        # create Keycloak URI for token login
        url: str = URI + REALM_PREFIX + REALM + AUTH_ENDPOINT
        keycloak_response: Response = self.send_request_to_keycloak(
            method="post", url=url, data=data
        )
        tokens_data: Dict[str, str] = keycloak_response.json()
        result: Dict[str, str] = {
            "access_token": tokens_data.get("access_token"),
            "refresh_token": tokens_data.get("refresh_token"),
        }
        return result

    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Refresh the access token using a refresh token.

        :param refresh_token: A string containing the refresh token.
        :type refresh_token: str
        :return: A dictionary containing the token and refresh token.
        :rtype: dict[str, str]
        :raises AssertionError: If the refresh token is missing.
        """
        assert refresh_token, constants.ASSERT_NULL_OBJECT

        request_data: Dict[str, str] = {
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": refresh_token,
        }
        url: str = URI + REALM_PREFIX + REALM + AUTH_ENDPOINT
        keycloak_response: Response = self.send_request_to_keycloak(
            method="post", url=url, data=request_data
        )
        data: Dict[str, str] = keycloak_response.json()
        return {
            "access_token": data.get("access_token"),
            "refresh_token": data.get("refresh_token"),
        }

    def create_user(self, obj_data: dict) -> dict:
        """
        Create a user in Keycloak.

        :param obj_data: A dictionary containing user data.
        :type obj_data: dict
        :return: The ID of the created user.
        :rtype: str
        :raises AssertionError: If the request data is missing or not a dict.
        """
        assert obj_data, constants.ASSERT_NULL_OBJECT
        assert isinstance(obj_data, dict), constants.ASSERT_DICT_OBJECT

        data: Dict[str, Any] = {
            "email": obj_data.get("email"),
            "username": obj_data.get("username"),
            "firstName": obj_data.get("first_name", " "),
            "lastName": obj_data.get("last_name", " "),
            "attributes": {
                "phone": obj_data.get("phone", " "),
                "birthdate": str(obj_data.get("birthdate", " ")),
                "national_id": obj_data.get("national_id", " "),
                "id_expiration": str(obj_data.get("id_expiration", " ")),
                "is_verified": obj_data.get("is_verified", " "),
                "last_active": obj_data.get("last_active", " "),
                "status": obj_data.get("status", " "),
                "is_deleted": obj_data.get("is_deleted", " "),
                "meta_data": obj_data.get("meta_data", " "),
            },
            "credentials": [
                {
                    "value": obj_data.get("password"),
                    "type": "password",
                    "temporary": False,
                }
            ],
            "enabled": True,
            "emailVerified": False,
            "access": {
                "manageGroupMembership": True,
                "view": True,
                "mapRoles": True,
                "impersonate": True,
                "manage": True,
            },
        }
        # reminder: create user
        self.keycloak_post(endpoint="/users", data=data)
        # reminder: get user details from Keycloak
        user: dict = self.get_keycloak_user(obj_data.get("username"))
        return user

    def update_user(self, obj_data: dict) -> dict:
        """
        Update a user in Keycloak.

        :param obj_data: A dictionary containing updated user data.
        :type obj_data: dict
        :return: The username of the updated user.
        :rtype: dict
        :raises AssertionError: If the request data is missing or not a dict.
        """
        assert obj_data, constants.ASSERT_NULL_OBJECT
        assert isinstance(obj_data, dict), constants.ASSERT_DICT_OBJECT

        user: dict = self.get_keycloak_user(obj_data.get("username"))
        user_attributes: dict = user.get("attributes")
        for field in obj_data:
            if field in user:
                user[field] = obj_data[field]
            elif field in user_attributes:
                user_attributes[field] = obj_data.get(field)
        # reminder: update user on Keycloak
        self.keycloak_put(endpoint=f"/users/{user.get('id')}", data=user)
        # reminder: get updated details from Keycloak
        updated_user: dict = self.get_keycloak_user(username=obj_data.get("username"))
        return updated_user

    # noinspection PyMethodMayBeStatic
    def auth_service_field(self, obj_id: str, obj_data: dict) -> dict:
        """
        Generate user data for the authentication service.

        :param obj_id: The ID of the account.
        :type obj_id: str
        :param obj_data: A dictionary containing account data.
        :type obj_data: dict
        :return: A dictionary containing user data for the authentication service.
        :rtype: dict
        :raises AssertionError: If the request data is missing or not a dict or
        the id is missing.
        """
        assert obj_id, constants.ASSERT_NULL_OBJECT
        assert obj_data, constants.ASSERT_NULL_OBJECT
        assert isinstance(obj_data, dict), constants.ASSERT_DICT_OBJECT

        user_data: dict = {"username": obj_id}
        for field in obj_data:
            auth_service_field = field.split("_")
            for index in range(len(auth_service_field)):
                if index > 0:
                    auth_service_field[index]: dict = auth_service_field[
                        index
                    ].capitalize()
            user_data["".join(auth_service_field)]: list = obj_data.get(field)
        user_data.update(obj_data)
        return user_data

    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user from Keycloak.

        :param user_id: The ID of the user to be deleted.
        :type user_id: str
        :return: True if the user is successfully deleted, False otherwise.
        :rtype: bool
        :raises AssertionError: If the user ID is missing.
        """
        assert user_id, constants.ASSERT_NULL_OBJECT

        # user ID is set as username in the authentication service
        user: dict = self.get_keycloak_user(user_id)
        endpoint: str = f"/users/{user.get('id')}"
        # delete user
        self.keycloak_delete(endpoint)
        return True

    def get_all_groups(self) -> List[Dict[str, str]]:
        """
        Retrieve all groups from Keycloak.

        :return: A list of dictionaries containing group information.
        :rtype: List[Dict[str, str]]
        """
        url: str = URI + ADMIN_REALM_URL + REALM + "/groups"
        keycloak_response: Response = self.send_request_to_keycloak(
            method="get", url=url, headers=self.get_keycloak_headers()
        )
        return keycloak_response.json()

    def get_keycloak_user(self, username: str) -> Union[dict, None]:
        """
        Retrieve a Keycloak user by username.

        :param username: The username of the Keycloak user.
        :type username: str
        :return: The user information as a dictionary, or None if the user is not found.
        :rtype: Union[dict, None]
        :raises AssertionError: If the username is missing.
        """
        assert username, constants.ASSERT_NULL_OBJECT

        url: str = URI + ADMIN_REALM_URL + REALM + "/users?username=" + username
        keycloak_response: Response = self.send_request_to_keycloak(
            method="get", url=url, headers=self.get_keycloak_headers()
        )
        user: list = keycloak_response.json()
        return user[0] if user else None

    def assign_group(self, user_id: str, group: dict) -> bool:
        """
        Assign a group to a user in Keycloak.

        :param user_id: The ID of the user to assign the group.
        :type user_id: str
        :param group: The group information to assign to the user.
        :type group: dict
        :return: True if the group is successfully assigned to the user.
        :rtype: bool
        :raises AssertionError: If the user ID or group is missing or group is not a dict
        """
        assert user_id, constants.ASSERT_NULL_OBJECT
        assert group, constants.ASSERT_NULL_OBJECT
        assert isinstance(group, dict), constants.ASSERT_DICT_OBJECT

        endpoint: str = "/users/" + user_id + "/groups/" + group.get("id")
        url: str = URI + ADMIN_REALM_URL + REALM + endpoint
        self.send_request_to_keycloak(
            method="put", url=url, headers=self.get_keycloak_headers()
        )
        return True

    def change_password(self, data: dict) -> bool:
        """
        Change the password for a user in Keycloak.

        :param data: The data for password reset.
        :type data: dict
        :return: True if the password is successfully changed.
        :rtype: bool
        :raises AssertionError: If the request data is missing or not a dict.
        """
        assert data, constants.ASSERT_NULL_OBJECT
        assert isinstance(data, dict), constants.ASSERT_DICT_OBJECT

        username: str = data.get("username")
        new_password: str = data.get("new_password")
        user: dict = self.get_keycloak_user(username)
        url: str = "/users/" + user.get("id") + "/reset-password"
        data: dict = {"type": "password", "value": new_password, "temporary": False}
        self.keycloak_put(url, data)
        return True

    def keycloak_post(self, endpoint: str, data: dict) -> Response:
        """
        Make a POST request to Keycloak.

        :param endpoint: Keycloak endpoint.
        :type endpoint: str
        :param data: Keycloak data object.
        :type data: object
        :return: Request response object.
        :rtype: Response
        :raises AssertionError: If the endpoint or data is
        missing or the data is not a dict.
        """
        assert endpoint, constants.ASSERT_NULL_OBJECT
        assert data, constants.ASSERT_NULL_OBJECT
        assert isinstance(data, dict), constants.ASSERT_DICT_OBJECT

        url: str = URI + ADMIN_REALM_URL + REALM + endpoint
        keycloak_response: Response = self.send_request_to_keycloak(
            method="post", url=url, headers=self.get_keycloak_headers(), json=data
        )
        return keycloak_response

    def keycloak_put(self, endpoint: str, data: dict) -> Response:
        """
        Make a PUT request to Keycloak.

        :param endpoint: Keycloak endpoint.
        :type endpoint: str
        :param data: Keycloak data object.
        :type data: object
        :return: Request response object.
        :rtype: Response
        :raises AssertionError: If the endpoint or data is
        missing or the data is not a dict.
        """
        assert endpoint, "Missing endpoint for put request"
        assert data, "Missing data for put request"

        url: str = URI + ADMIN_REALM_URL + REALM + endpoint
        keycloak_response: Response = self.send_request_to_keycloak(
            method="put", url=url, headers=self.get_keycloak_headers(), json=data
        )
        return keycloak_response

    def keycloak_delete(self, endpoint: str) -> Response:
        """
        Make a DELETE request to Keycloak.

        :param endpoint: Keycloak endpoint.
        :type endpoint: str
        :return: Request response object.
        :rtype: Response
        :raises AssertionError: If the endpoint is missing.
        """
        assert endpoint, constants.ASSERT_NULL_OBJECT

        url: str = URI + ADMIN_REALM_URL + REALM + endpoint
        keycloak_response: Response = self.send_request_to_keycloak(
            method="delete", url=url, headers=self.get_keycloak_headers()
        )
        return keycloak_response

    def get_keycloak_headers(self) -> dict:
        """
        Login as an admin user into Keycloak and use the access token as an
        authentication user.

        :return: Object of Keycloak headers.
        :rtype: dict
        """
        realm_admin = {
            "username": settings.keycloak_admin_username,
            "password": settings.keycloak_admin_password,
        }
        token: dict = self.get_token(realm_admin)
        headers = {
            "Authorization": "Bearer " + token.get("access_token"),
            "Content-Type": "application/json",
        }
        return headers

    def realm_openid_configuration(self) -> dict:
        """
        Returns all OpenID configuration URL endpoints pertaining to the admin realm.

        :return: URL endpoints.
        :rtype: dict

        :raises AppException.KeyCloakAdminException: If the Keycloak response status
        code is not OK.
        """
        url: str = URI + REALM_URL + OPENID_CONFIGURATION_ENDPOINT
        keycloak_response: Response = self.send_request_to_keycloak(
            method="get", url=url
        )
        data = keycloak_response.json()
        return data

    # noinspection PyMethodMayBeStatic
    def send_request_to_keycloak(
        self,
        method: str,
        url: str,
        headers: Optional[dict] = None,
        json: Optional[dict] = None,
        data: Optional[dict] = None,
    ) -> Response:
        """
        Sends a request to the Keycloak server.

        :param method: HTTP method for the request.
        :type method: str
        :param url: URL of the request.
        :type url: str
        :param headers: Headers for the request.
        :type headers: dict
        :param json: JSON data for the request body.
        :type json: dict
        :param data: Data for the request body.
        :type data: dict

        :return: Response object from the Keycloak server.
        :rtype: Response

        :raises AppException.ServiceRequestException: If an error occurs
        while connecting to the Keycloak server.
        """

        try:
            response = requests.request(
                method=method, url=url, headers=headers, json=json, data=data
            )
            if response.status_code >= 300:
                raise AppException.ServiceRequestException(
                    status_code=response.status_code,
                    error_message=response.json(),
                    context=get_error_context(
                        module=__name__,
                        method=inspect.currentframe().f_code.co_name,
                        calling_module=str(inspect.stack()[1]),
                        calling_method=inspect.currentframe().f_back.f_code.co_name,
                        error=response.json(),
                    ),
                )
            return response
        except exceptions.RequestException as exc:
            raise AppException.ServiceRequestException(
                error_message="error connecting to keycloak server",
                context=get_error_context(
                    exc_class=get_full_class_name(exc),
                    module=__name__,
                    method=inspect.currentframe().f_code.co_name,
                    calling_module=str(inspect.stack()[1]),
                    calling_method=inspect.currentframe().f_back.f_code.co_name,
                    error=str(exc),
                ),
            )
