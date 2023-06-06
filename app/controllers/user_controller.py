import random
import secrets
from datetime import datetime, timedelta
from string import digits
from typing import Any, Dict, List, Optional

import pytz
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Query

from app import constants
from app.core.exceptions import AppException
from app.core.notifications import Notifier
from app.models import UserModel, UserOtpModel
from app.notifications import EmailNotificationHandler, SMSNotificationHandler
from app.repositories import UserOtpRepository, UserRepository
from app.services import KeycloakAuthService

utc = pytz.UTC


class UserController(Notifier):
    def __init__(
        self,
        user_repository: UserRepository,
        keycloak_auth_service: KeycloakAuthService,
        user_otp_repository: UserOtpRepository,
    ):
        """
        Initialize the UserController.

        :param user_repository: The user repository object.
        :type user_repository: UserRepository
        :param user_otp_repository: The user otp repository object.
        :type user_otp_repository: UserOtpRepository
        :param keycloak_auth_service: The KeycloakAuthService object.
        :type keycloak_auth_service: KeycloakAuthService
        """
        self.user_repository = user_repository
        self.user_otp_repository = user_otp_repository
        self.keycloak_auth_service = keycloak_auth_service

    # noinspection PyMethodMayBeStatic
    def get_all_users(self, **kwargs) -> paginate:
        """
        Get all users based on the provided arguments.

        :param kwargs: Additional keyword arguments for filtering, sorting,
        and pagination. Supported keyword arguments:
                       - search: Search keyword for filtering users.
                       - sort_in: Sorting direction, either 'asc' or 'desc'.
                       - order_by: Field name to order the users by.
                       - is_deleted: Flag to filter deleted users.
                       - paginate: Pagination parameters.
        :type kwargs: Any
        :return: A list of SampleModel instances representing the retrieved users.
        :rtype: paginate
        """
        query_result: Query = UserModel.search(keyword=kwargs.get("search"))
        query_result: Query = UserModel.filter(
            query_result=query_result,
            filter_param={"is_deleted": kwargs.get("is_deleted")},
        )
        query_result: Query = UserModel.sort(
            query_result=query_result,
            sort_in=kwargs.get("sort_in"),
            order_by=kwargs.get("order_by"),
        )
        result: paginate = UserModel.paginate(
            query_result=query_result, pagination=kwargs.get("paginate")
        )
        return result

    def get_user(self, obj_id: str) -> UserModel:
        """
        Get a user based on the provided id.

        :param obj_id: The id of the user to query for.
        :type obj_id: uuid.UUID
        :return: The retrieved SampleModel instance.
        :rtype: SampleModel
        :raises AppException.NotFoundException: If the resource does not exist.
        :raises AssertionError: If `obj_id` is empty or None.
        """
        assert obj_id, constants.ASSERT_NULL_OBJECT

        try:
            result: UserModel = self.user_repository.find_by_id(obj_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=constants.EXC_NOT_FOUND.format("user")
            )
        return result

    def create_user(self, obj_data: dict) -> UserModel:
        """
        Create a new user based on the provided data.

        :param obj_data: The properties of the new user.
        :type obj_data: dict
        :return: The created UserModel instance.
        :rtype: UserModel
        :raises AssertionError: If `obj_data` is not a dictionary or is empty or None.
        """
        assert isinstance(obj_data, dict), constants.ASSERT_DICT_OBJECT
        assert obj_data, constants.ASSERT_NULL_OBJECT

        password: str = obj_data.pop("password")
        obj_data["hash_password"] = password
        result: UserModel = self.user_repository.create(obj_data)
        obj_data["password"] = password
        auth_user: dict = self.keycloak_auth_service.create_user(obj_data=obj_data)
        self.user_repository.update_by_id(
            obj_id=result.id, obj_in={"auth_provider_id": auth_user.get("id")}
        )
        return result

    def update_user(self, obj_id: str, obj_data: dict) -> UserModel:
        """
        Update a user with the provided ID using the given data.

        :param obj_id: The ID of the user to update.
        :type obj_id: str
        :param obj_data: The data to update the user with.
        :type obj_data: dict
        :return: The updated UserModel instance.
        :rtype: UserModel
        :raises AssertionError: If `obj_data` is not a dictionary or is empty or None,
        or if `obj_id` is empty or None.
        :raises AppException.NotFoundException: If the user with the given
        ID is not found.
        """
        assert isinstance(obj_data, dict), constants.ASSERT_DICT_OBJECT
        assert obj_data, constants.ASSERT_NULL_OBJECT
        assert obj_id, constants.ASSERT_NULL_OBJECT

        obj_data: dict = {key: value for key, value in obj_data.items() if value}
        try:
            result: UserModel = self.user_repository.update_by_id(
                obj_id=obj_id, obj_in=obj_data
            )
            auth_provider_fields: dict = self.keycloak_auth_service.auth_service_field(
                obj_id=result.username, obj_data=obj_data
            )
            self.keycloak_auth_service.update_user(obj_data=auth_provider_fields)
            return result
        except AppException.NotFoundException:
            raise AppException.NotFoundException(error_message=constants.EXC_NOT_FOUND)

    def delete_user(self, obj_id: str) -> None:
        """
        Delete a user with the provided ID.

        :param obj_id: The ID of the user to delete.
        :type obj_id: str
        :raises AssertionError: If `obj_id` is empty or None.
        :raises AppException.NotFoundException: If the user with the
        given ID is not found.
        :return: None
        """
        assert obj_id, constants.ASSERT_NULL_OBJECT

        disable_user: dict = {
            "is_deleted": True,
            "enabled": False,
            "deleted_at": datetime.now(),
        }
        try:
            result: UserModel = self.user_repository.update_by_id(
                obj_id=obj_id, obj_in=disable_user
            )
            auth_provider_fields: dict = self.keycloak_auth_service.auth_service_field(
                obj_id=result.username, obj_data=disable_user
            )
            self.keycloak_auth_service.update_user(obj_data=auth_provider_fields)
            return None
        except AppException.NotFoundException:
            raise AppException.NotFoundException(error_message=constants.EXC_NOT_FOUND)

    def user_profile(self, auth_user: dict) -> UserModel:
        """
        Get the user profile based on the authenticated user.

        :param auth_user: The dictionary containing user information, including the ID.
        :type auth_user: dict
        :return: The user profile information.
        :rtype: UserModel
        :raises AssertionError: If the authenticated user data is empty or
        not a dictionary.
        :raises AppException.NotFoundException: If the user with the given ID
        is not found.
        """

        assert auth_user, constants.ASSERT_NULL_OBJECT
        assert isinstance(auth_user, dict), constants.ASSERT_DICT_OBJECT

        try:
            return self.user_repository.find({"username": auth_user.get("username")})
        except AppException.NotFoundException:
            raise AppException.NotFoundException(error_message=constants.EXC_NOT_FOUND)

    def user_login(self, obj_data: dict) -> Dict:
        """
        Log in a user with the provided credentials.

        :param obj_data: The login credentials.
        :type obj_data: dict
        :return: The authentication result.
        :rtype: dict
        :raises AssertionError: If the provided obj_data is not a dictionary or is empty.
        :raises AppException.BadRequestException: If the credentials are invalid
        or not found.
        """
        assert isinstance(obj_data, dict), constants.ASSERT_DICT_OBJECT
        assert obj_data, constants.ASSERT_NULL_OBJECT

        try:
            user_account: UserModel = self.user_repository.find(
                filter_param={"username": obj_data.get("username")}
            )
            if not user_account.verify_password(obj_data.get("password")):
                raise AppException.BadRequestException(
                    error_message=constants.EXC_INVALID_INPUT.format("credentials")
                )
            result: dict = self.keycloak_auth_service.get_token(
                obj_data={
                    "username": user_account.username,
                    "password": obj_data.get("password"),
                }
            )
            result["user_id"] = user_account.id
            return result
        except AppException.NotFoundException:
            raise AppException.BadRequestException(
                error_message=constants.EXC_INVALID_INPUT.format("credentials")
            )

    def refresh_user_token(self, obj_data: dict) -> Dict:
        """
        Refreshes a user's authentication token.

        :param obj_data: The data for refreshing the user token.
        :type obj_data: dict
        :return: The result of the token refresh operation.
        :rtype: dict
        :raises AssertionError: If obj_data is not a dict or if it is an empty dict.
        """
        assert isinstance(obj_data, dict), constants.ASSERT_DICT_OBJECT
        assert obj_data, constants.ASSERT_NULL_OBJECT

        user_id: str = obj_data.get("user_id")
        try:
            self.user_repository.find_by_id(user_id)
            result: dict = self.keycloak_auth_service.refresh_token(
                refresh_token=obj_data.get("refresh_token")
            )
            result["user_id"] = user_id
            return result
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=constants.EXC_NOT_FOUND.format("user")
            )

    def verify_phone(self, auth_user: Dict[str, Any], obj_data: Dict[str, Any]) -> Dict:
        """
        Request to change the phone number of the authenticated user.

        :param auth_user: The dictionary containing the authenticated user information.
        :type auth_user: dict
        :param obj_data: The dictionary containing the new phone number.
        :type obj_data: dict
        :return: The schema containing the user ID.
        :rtype: dict
        :raises AssertionError: If the obj_data or auth_user is empty or
        not a dictionary.
        :raises AppException.ResourceExistsException: If the new phone number already
        exists in the user repository.
        :raises AppException.NotFoundException: If the user with the given username
        is not found.
        """
        assert isinstance(obj_data, dict), constants.ASSERT_DICT_OBJECT
        assert obj_data, constants.ASSERT_NULL_OBJECT
        assert auth_user, constants.ASSERT_NULL_OBJECT
        assert isinstance(auth_user, dict), constants.ASSERT_DICT_OBJECT

        new_phone: str = obj_data.get("new_phone")
        username: str = auth_user.get("username")
        try:
            self.user_repository.find({"phone": new_phone})
            raise AppException.ResourceExistsException(
                error_message=constants.EXC_FOUND.format("phone")
            )
        except AppException.NotFoundException:
            try:
                user: UserModel = self.user_repository.find({"username": username})
                otp_code: str = self.__generate_otp_code(length=6)
                sec_code: str = self.__generate_security_code(16)
                expiration: datetime = datetime.now() + timedelta(minutes=5)
                self.__create_otp_record(
                    user_id=user.id,
                    otp_code=otp_code,
                    sec_code=sec_code,
                    expiration=expiration,
                )
                self.__sms_otp(code=otp_code, phone=[new_phone])
                self.__email_otp(code=otp_code, email=[user.email])
                return {"user_id": user.id}
            except AppException.NotFoundException:
                raise AppException.NotFoundException(
                    error_message=constants.EXC_NOT_FOUND.format("username")
                )

    def change_phone(self, auth_user: dict, obj_data: dict) -> Dict:
        """
        Change the phone number of the authenticated user.

        :param auth_user: The dictionary containing the authenticated user information.
        :type auth_user: dict
        :param obj_data: The dictionary containing the new phone number and OTP code.
        :type obj_data: dict
        :return: The schema containing the user ID.
        :rtype: dict
        :raises AssertionError: If the obj_data or auth_user is empty or
        not a dictionary.
        :raises AppException.NotFoundException: If the user with the given
        username is not found.
        """
        assert isinstance(obj_data, dict), constants.ASSERT_DICT_OBJECT
        assert obj_data, constants.ASSERT_NULL_OBJECT
        assert auth_user, constants.ASSERT_NULL_OBJECT
        assert isinstance(auth_user, dict), constants.ASSERT_DICT_OBJECT

        try:
            user: UserModel = self.user_repository.find(
                {"username": auth_user.get("username")}
            )
            self.__confirm_sec_token(
                user_id=user.id, sec_token=obj_data.get("sec_token")
            )
            self.update_user(
                obj_id=user.id, obj_data={"phone": obj_data.get("new_phone")}
            )
            self.__create_otp_record(user_id=user.id)
            return {"user_id": user.id}
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=constants.EXC_NOT_FOUND.format("username")
            )

    def change_user_password(self, auth_user: dict, obj_data: dict) -> Dict:
        """
        Change the password of the authenticated user.

        :param auth_user: The dictionary containing the authenticated user data.
        :type auth_user: dict
        :param obj_data: The dictionary containing the new password data.
        :type obj_data: dict
        :return: The schema containing the user ID.
        :rtype: dict
        :raises AssertionError: If the obj_data or auth_user is empty or
        not a dictionary.
        :raises AppException.NotFoundException: If the user is not found.
        :raises AppException.BadRequestException: If the provided credentials
        are invalid.
        """
        assert isinstance(obj_data, dict), constants.ASSERT_DICT_OBJECT
        assert obj_data, constants.ASSERT_NULL_OBJECT
        assert isinstance(auth_user, dict), constants.ASSERT_DICT_OBJECT
        assert auth_user, constants.ASSERT_NULL_OBJECT

        sec_token: str = obj_data.get("sec_token")
        old_password: str = obj_data.get("old_password")
        new_password: str = obj_data.get("new_password")
        try:
            user: UserModel = self.user_repository.find(
                filter_param={"username": auth_user.get("username")}
            )
            self.__confirm_sec_token(user_id=user.id, sec_token=sec_token)
            if not user.verify_password(old_password):
                raise AppException.BadRequestException(
                    error_message=constants.EXC_INVALID_INPUT.format("credentials")
                )
            self.user_repository.update_by_id(
                obj_id=user.id, obj_in={"hash_password": new_password}
            )
            self.keycloak_auth_service.change_password(
                data={"username": user.username, "new_password": new_password}
            )
            self.__create_otp_record(user_id=user.id)
            return {"user_id": user.id}
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=constants.EXC_NOT_FOUND.format("user")
            )

    def reset_user_password(self, obj_data: dict) -> Dict:
        """
        Change the password of a user.

        :param obj_data: The dictionary containing the user ID, security token,
        and new password.
        :type obj_data: dict
        :return: The schema containing the user ID.
        :rtype: dict
        :raises AppException.NotFoundException: If the user account does not exist.
        :raises AssertionError: If the obj_data parameter is not a dictionary
        or is empty.
        """
        assert isinstance(obj_data, dict), constants.ASSERT_DICT_OBJECT
        assert obj_data, constants.ASSERT_NULL_OBJECT

        user_id: str = str(obj_data.get("user_id"))
        sec_token: str = obj_data.get("sec_token")
        new_password: str = obj_data.get("new_password")
        try:
            user: UserModel = self.user_repository.find_by_id(obj_id=user_id)
            self.__confirm_sec_token(user_id=user_id, sec_token=sec_token)
            self.user_repository.update_by_id(
                obj_id=user.id, obj_in={"hash_password": new_password}
            )
            self.keycloak_auth_service.change_password(
                data={"username": user.username, "new_password": new_password}
            )
            self.__create_otp_record(user_id=user.id)
            return {"user_id": user.id}
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=constants.EXC_NOT_FOUND.format("user")
            )

    def send_otp_code(self, sms: bool, email: bool, obj_data: dict) -> Dict:
        """
        Send an OTP (one-time password) code to the user via the specified
        notification channels.

        :param sms: If True, send the OTP via SMS.
        :type sms: bool
        :param email: If True, send the OTP via email.
        :type email: bool
        :param obj_data: The dictionary containing the user data for sending OTP.
        :type obj_data: dict
        :return: The schema containing the user ID.
        :rtype: dict
        :raises AssertionError: If the obj_data is empty or not a dictionary.
        :raises AppException.BadRequestException: If both sms and email parameters
        are False.
        :raises AppException.NotFoundException: If the user is not found.
        """
        assert obj_data, constants.ASSERT_NULL_OBJECT
        assert isinstance(obj_data, dict), constants.ASSERT_DICT_OBJECT

        obj_data["id"] = obj_data.pop("user_id", None)
        if not sms and not email:
            raise AppException.BadRequestException(
                error_message=constants.EXC_INVALID_INPUT.format("notification channel")
            )
        filter_param: dict = {
            key: value for key, value in obj_data.items() if value is not None
        }
        try:
            user: UserModel = self.user_repository.find(filter_param=filter_param)
            otp_code: str = self.__generate_otp_code(length=6)
            sec_code: str = self.__generate_security_code(16)
            expiration: datetime = datetime.now() + timedelta(minutes=5)
            self.__create_otp_record(
                user_id=user.id,
                otp_code=otp_code,
                sec_code=sec_code,
                expiration=expiration,
            )
            self.__sms_otp(code=otp_code, phone=[user.phone]) if sms else None
            self.__email_otp(code=otp_code, email=[user.email]) if email else None
            return {"user_id": user.id}
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=constants.EXC_NOT_FOUND.format("user")
            )

    # noinspection PyMethodMayBeStatic
    def confirm_otp_code(self, obj_data: dict) -> Dict:
        """
        Confirm the OTP (one-time password) code provided by the user.

        :param obj_data: The dictionary containing the OTP code and user ID.
        :type obj_data: dict
        :return: The schema containing the user ID and security token.
        :rtype: dict
        :raises AssertionError: If the obj_data is empty or not a dictionary.
        :raises AppException.InvalidTokenException: If the OTP code is invalid
        or expired.
        :raises AppException.NotFoundException: If the OTP record with the given user
        ID is not found.
        """
        assert isinstance(obj_data, dict), constants.ASSERT_DICT_OBJECT
        assert obj_data, constants.ASSERT_NULL_OBJECT

        otp: str = obj_data.get("otp_code")
        try:
            otp_record: UserOtpModel = self.user_otp_repository.find(
                {"user_id": obj_data.get("user_id")}
            )
            if otp_record.otp_code != otp and otp not in constants.MASTER_OTP_CODE:
                raise AppException.InvalidTokenException(
                    error_message=constants.EXC_INVALID_INPUT.format("otp code")
                )
            if utc.localize(datetime.now()) > otp_record.otp_code_expiration:
                raise AppException.InvalidTokenException(
                    error_message=constants.EXC_EXPIRED_INPUT.format("otp code")
                )
            return {"user_id": otp_record.id, "sec_token": otp_record.sec_token}
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=constants.EXC_NOT_FOUND.format("otp record")
            )

    def __confirm_sec_token(self, user_id: str, sec_token: str) -> UserOtpModel:
        """
        Confirm the security token for a user.

        :param user_id: The ID of the user.
        :type user_id: str
        :param sec_token: The security token to confirm.
        :type sec_token: str
        :return: The UserOtpModel object representing the confirmed security token.
        :rtype: UserOtpModel
        :raises AppException.NotFoundException: If the OTP record for the user
        is not found.
        :raises AppException.InvalidTokenException: If the provided security token
        is invalid or expired.
        :raises AssertionError: If the user_id or sec_token parameters are empty or None.
        """
        assert user_id, constants.ASSERT_NULL_OBJECT
        assert sec_token, constants.ASSERT_NULL_OBJECT

        try:
            result: UserOtpModel = self.user_otp_repository.find({"user_id": user_id})
            if result.sec_token != sec_token:
                raise AppException.InvalidTokenException(
                    error_message=constants.EXC_INVALID_INPUT.format("security token")
                )
            if utc.localize(datetime.now()) > result.sec_token_expiration:
                raise AppException.InvalidTokenException(
                    error_message=constants.EXC_EXPIRED_INPUT.format("security token")
                )
            return result
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=constants.EXC_NOT_FOUND.format("otp record")
            )

    def __create_otp_record(
        self,
        user_id: str,
        otp_code: Optional[str] = None,
        sec_code: Optional[str] = None,
        expiration: Optional[datetime] = None,
    ) -> UserOtpModel:
        """
        Create or update an OTP record for a user.

        :param user_id: The ID of the user.
        :type user_id: str
        :param otp_code: The OTP code.
        :type otp_code: str, optional
        :param sec_code: The security code.
        :type sec_code: str, optional
        :param expiration: The expiration datetime of the OTP record.
        :type expiration: datetime, optional
        :return: The UserOtpModel object representing the created or updated OTP record.
        :rtype: UserOtpModel
        :raises AppException.NotFoundException: If the OTP record for the user is
        not found during update.
        :raises AssertionError: If the user_id parameter is empty or None.
        """
        assert user_id, constants.ASSERT_NULL_OBJECT

        obj_data = {
            "otp_code": otp_code,
            "otp_code_expiration": expiration,
            "sec_token": sec_code,
            "sec_token_expiration": expiration,
        }
        try:
            result: UserOtpModel = self.user_otp_repository.update(
                filter_params={"user_id": user_id}, obj_in=obj_data
            )
        except AppException.NotFoundException:
            obj_data["user_id"] = user_id
            result: UserOtpModel = self.user_otp_repository.create(obj_in=obj_data)
        return result

    # noinspection PyMethodMayBeStatic
    def __generate_otp_code(self, length: int) -> str:
        """
        Generate a random OTP (one-time password) code of the specified length.

        :param length: The length of the OTP code.
        :type length: int
        :return: The generated OTP code.
        :rtype: str
        :raises AssertionError: If the length is empty or None.
        """
        assert length, constants.ASSERT_NULL_OBJECT

        return "".join(random.choices(digits, k=length))

    # noinspection PyMethodMayBeStatic
    def __generate_security_code(self, length: int) -> str:
        """
        Generate a random security code of the specified length.

        :param length: The length of the security code.
        :type length: int
        :return: The generated security code.
        :rtype: str
        :raises AssertionError: If the length is empty or None.
        """
        assert length, constants.ASSERT_NULL_OBJECT

        return secrets.token_urlsafe(length)

    def __email_otp(self, code: str, email: List[str]) -> None:
        """
        Send an Email with the provided OTP code to the given email addresses.

        :param code: The OTP code.
        :type code: str
        :param email: The list of email addresses to send the email to.
        :type email: List[str]
        :raises AssertionError: If the email list or the code is empty or None.
        """
        assert email, constants.ASSERT_LIST_OBJECT
        assert code, constants.ASSERT_NULL_OBJECT

        self.notify(
            EmailNotificationHandler(
                recipients=email,
                details={"otp_code": code},
                meta={
                    "type": "email_notification",
                    "subtype": "otp",
                },
            )
        )

    def __sms_otp(self, code: str, phone: List[str]) -> None:
        """
        Send an SMS with the provided OTP code to the given phone numbers.

        :param code: The OTP code.
        :type code: str
        :param phone: The list of phone numbers to send the SMS to.
        :type phone: List[str]
        :raises AssertionError: If the phone list or the code is empty or None.
        """
        assert phone, constants.ASSERT_LIST_OBJECT
        assert code, constants.ASSERT_NULL_OBJECT

        self.notify(
            SMSNotificationHandler(
                recipients=phone,
                details={"otp_code": code},
                meta={
                    "type": "sms_notification",
                    "subtype": "otp",
                },
            )
        )
