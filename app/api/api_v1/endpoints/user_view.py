import uuid
from typing import Dict, Optional

import pinject
from fastapi import APIRouter, Depends, status

from app.controllers import UserController
from app.enums import SortResultEnum
from app.repositories import UserOtpRepository, UserRepository
from app.schema import (
    CreateUserSchema,
    UpdateUserSchema,
    UserChangePasswordSchema,
    UserChangePhoneSchema,
    UserIdSchema,
    UserLoginResponseSchema,
    UserLoginSchema,
    UserOtpConfirmationResponseSchema,
    UserOtpConfirmationSchema,
    UserPhoneVerificationSchema,
    UserResetPasswordSchema,
    UserSchema,
    UserSendOtpSchema,
    UserTokenRefreshSchema,
)
from app.services import KeycloakAuthService, RedisService
from app.utils import (
    KeycloakJwtAuthentication,
    Page,
    Params,
    data_responses,
    query_responses,
)

user_router = APIRouter()
user_base_url = "/api/v1/users"

obj_graph = pinject.new_object_graph(
    modules=None,
    classes=[
        UserController,
        UserRepository,
        UserOtpRepository,
        RedisService,
        KeycloakAuthService,
    ],
)
user_controller: UserController = obj_graph.provide(UserController)


@user_router.get("", response_model=Page[UserSchema], responses=query_responses)
def get_all_users(
    search: Optional[str] = "",
    sort_in: Optional[SortResultEnum] = SortResultEnum.asc,
    order_by: Optional[str] = None,
    is_deleted: Optional[bool] = False,
    paginate: Params = Depends(),  # noqa
    current_user: dict = Depends(KeycloakJwtAuthentication()),  # noqa
) -> Page[UserSchema]:
    """
    Retrieve all users in the system based on the provided queries.

    :param paginate: The pagination parameters.
    :type paginate: Params, optional
    :param search: The search keyword.
    :type search: str, optional
    :param sort_in: The sorting direction.
    :type sort_in: QuerySortEnum, optional
    :param order_by: The attribute to sort by.
    :type order_by: str, optional
    :param is_deleted: Flag to include deleted users.
    :type is_deleted: bool, optional
    :param current_user: The current user making the get request.
    :type current_user: dict
    :return: The result of retrieving all users
    :rtype: Page[SampleSchema]
    """
    return user_controller.get_all_users(
        search=search,
        sort_in=sort_in,
        order_by=order_by,
        is_deleted=is_deleted,
        paginate=paginate,
    )


@user_router.get("/{user_id}", response_model=UserSchema, responses=query_responses)
def get_user(
    user_id: uuid.UUID, current_user: dict = Depends(KeycloakJwtAuthentication())  # noqa
) -> UserSchema:
    """
    Retrieve a user based on the user's id.

    :param user_id: The id of the resource to retrieve.
    :type user_id: uuid.UUID
    :param current_user: The current user making the get request.
    :type current_user: dict
    :return: The result of retrieving the user.
    :rtype: SampleSchema
    """
    return user_controller.get_user(str(user_id))


@user_router.post(
    "",
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
    responses={**data_responses, **query_responses},
)
def create_user(obj_data: CreateUserSchema) -> UserSchema:
    """
    Create a user.

    :param obj_data: The data for creating the user.
    :type obj_data: CreateSampleSchema
    :return: The result of creating the user.
    :rtype: SampleSchema
    """

    return user_controller.create_user(obj_data.dict())


@user_router.patch(
    "/{user_id}",
    response_model=UserSchema,
    responses={**data_responses, **query_responses},
)
def update_user(
    user_id: uuid.UUID,
    obj_data: UpdateUserSchema,
    current_user: dict = Depends(KeycloakJwtAuthentication()),  # noqa
) -> UserSchema:
    """
    Update a user based on the user's id.

    :param user_id: The id of the user to update.
    :type user_id: uuid.UUID
    :param obj_data: The data for updating the user.
    :type obj_data: UpdateUserSchema
    :param current_user: The current user making the update request.
    :type current_user: dict
    :return: The result of updating the user.
    :rtype: UserSchema
    """
    return user_controller.update_user(str(user_id), obj_data.dict())


@user_router.delete(
    "/{user_id}", status_code=status.HTTP_204_NO_CONTENT, responses=query_responses
)
def delete_user(
    user_id: uuid.UUID, current_user: dict = Depends(KeycloakJwtAuthentication())  # noqa
) -> None:
    """
    Delete a resource based on the resource's id.

    :param user_id: The id of the resource to delete.
    :type user_id: uuid.UUID
    :param current_user: The current user making the delete request.
    :type current_user: dict
    :return: The result of deleting the user.
    :rtype: None
    """
    return user_controller.delete_user(str(user_id))


@user_router.post("/token/access", response_model=UserLoginResponseSchema)
def user_login(obj_data: UserLoginSchema) -> Dict:
    """
    Perform user login with the provided user data.

    :param obj_data: The user data for login.
    :type obj_data: UserLoginSchema
    :return: The result of the user login operation.
    :rtype: dict
    """
    return user_controller.user_login(obj_data.dict())


@user_router.get("/account/profile", responses=query_responses)
def user_profile(
    current_user: dict = Depends(KeycloakJwtAuthentication()),  # noqa
) -> UserSchema:
    """
    Get the user profile for the current user.

    :param current_user: The current user's information obtained from authentication.
    :type current_user: dict
    :return: UserSchema
    """
    return user_controller.user_profile(current_user)


@user_router.post("/token/refresh", response_model=UserLoginResponseSchema)
def refresh_token(obj_data: UserTokenRefreshSchema) -> Dict:
    """
    Refresh the user token with the provided data.

    :param obj_data: The data for refreshing the user token.
    :type obj_data: UserTokenRefreshSchema
    :return: The result of the token refresh operation.
    :rtype: dict
    """
    return user_controller.refresh_user_token(obj_data.dict())


@user_router.post("/update/phone/verify", response_model=UserIdSchema)
def verify_phone(
    obj_data: UserPhoneVerificationSchema,
    current_user: dict = Depends(KeycloakJwtAuthentication()),  # noqa
) -> Dict:
    """
    Verify a new phone number for a user.

    :param obj_data: The data for verifying the new phone number.
    :type obj_data: SampleSchema
    :param current_user: The current user obtained from authentication.
    :type current_user: dict
    :return: The result of the phone verification operation.
    :rtype: dict
    """
    return user_controller.verify_phone(current_user, obj_data.dict())


@user_router.post("/update/phone", response_model=UserIdSchema)
def change_phone(
    obj_data: UserChangePhoneSchema,
    current_user: dict = Depends(KeycloakJwtAuthentication()),  # noqa
) -> Dict:
    """
    Change the phone number for a user.

    :param obj_data: The data for changing the phone number.
    :type obj_data: SampleSchema
    :param current_user: The current user obtained from authentication.
    :type current_user: dict
    :return: The result of the phone number change operation.
    :rtype: dict
    """
    return user_controller.change_phone(current_user, obj_data.dict())


@user_router.post("/update/password", response_model=UserIdSchema)
def change_password(
    obj_data: UserChangePasswordSchema,
    current_user: dict = Depends(KeycloakJwtAuthentication()),  # noqa
) -> Dict:
    """
    Change the password for a user.

    :param obj_data: The data for changing the password.
    :type obj_data: UserChangePasswordSchema
    :param current_user: The current user obtained from authentication.
    :type current_user: dict
    :return: The result of the password change operation.
    :rtype: dict
    """
    return user_controller.change_user_password(current_user, obj_data.dict())


@user_router.post("/update/password/reset", response_model=UserIdSchema)
def reset_password(obj_data: UserResetPasswordSchema) -> Dict:
    """
    Reset the password for a user.

    :param obj_data: The data for resetting the password.
    :type obj_data: UserResetPasswordSchema
    :return: The result of the password reset operation.
    :rtype: dict
    """
    return user_controller.reset_user_password(obj_data.dict())


@user_router.post("/otp/send", response_model=UserIdSchema)
def send_otp(
    obj_data: UserSendOtpSchema, sms: Optional[bool] = None, email: Optional[bool] = None
) -> Dict:
    """
    Send an OTP (one-time password) code to the user.

    :param obj_data: The schema containing the user data for sending OTP.
    :type obj_data: UserSendOtpSchema
    :param sms: If True, send the OTP via SMS.
    :type sms: bool, optional
    :param email: If True, send the OTP via email.
    :type email: bool, optional
    :return: The schema containing the user ID.
    :rtype: dict
    """
    return user_controller.send_otp_code(sms, email, obj_data.dict())


@user_router.post("/otp/confirm", response_model=UserOtpConfirmationResponseSchema)
def confirm_otp(obj_data: UserOtpConfirmationSchema) -> Dict:
    """
    Confirm an OTP (One-Time Password) entered by a user.

    :param obj_data: The data for confirming the OTP.
    :type obj_data: UserOtpConfirmationSchema
    :return: The result of the OTP confirmation operation.
    :rtype: dict
    """
    return user_controller.confirm_otp_code(obj_data.dict())
