# -*- coding: utf-8 -*-
"""
JWT Authentication Middleware
用于HTML视图自动认证用户，从Authorization header中解析JWT token
"""
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.request import Request
from django.http import HttpRequest

User = get_user_model()


class JWTAuthenticationMiddleware:
    """
    Middleware to authenticate users from JWT tokens in the Authorization header.
    This allows HTML views to recognize authenticated users when they have a valid JWT token.

    The middleware:
    1. Extracts the JWT token from the Authorization header
    2. Validates the token using DRF's JWTAuthentication
    3. Sets request.user to the authenticated user
    4. Allows views to access user information (balance, payment_password, etc.)
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()

    def __call__(self, request):
        # Try to authenticate the user from JWT token
        self.authenticate_jwt(request)

        response = self.get_response(request)
        return response

    def authenticate_jwt(self, request):
        """
        Attempt to authenticate the user from the JWT token in the Authorization header.
        If successful, sets request.user to the authenticated user.
        If unsuccessful or no token present, leaves request.user as AnonymousUser.
        """
        try:
            # Get the Authorization header
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')

            if not auth_header.startswith('Bearer '):
                # No JWT token in header, skip authentication
                return

            # Create a DRF Request object to use with JWTAuthentication
            # We need to do this because JWTAuthentication expects a DRF Request
            drf_request = Request(request)

            # Attempt to authenticate using JWT
            auth_result = self.jwt_auth.authenticate(drf_request)

            if auth_result is not None:
                # Successfully authenticated
                user, validated_token = auth_result
                request.user = user
                request.auth = validated_token

                # Optional: Log successful authentication
                # print(f"[JWT Middleware] User authenticated: {user.username}")

        except (InvalidToken, TokenError) as e:
            # Token is invalid or expired, leave request.user as AnonymousUser
            # Optional: Log the error
            # print(f"[JWT Middleware] Token validation failed: {e}")
            pass
        except Exception as e:
            # Other errors, just skip authentication
            # Optional: Log the error for debugging
            # print(f"[JWT Middleware] Unexpected error: {e}")
            pass
