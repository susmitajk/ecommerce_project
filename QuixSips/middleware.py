from django.contrib.auth import logout
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
import logging

class BlockUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)  # Initialize logger

    def __call__(self, request):
        self.logger.debug("BlockUserMiddleware executing...")
        self.logger.debug(f"User type: {type(request.user)}")  # Check the type of request.user

        # Check if request.user is authenticated and has the necessary attributes
        if request.user.is_authenticated:
            self.logger.debug(f"is_active: {request.user.is_active}")
            if hasattr(request.user, 'is_reactivated'):
                self.logger.debug(f"is_reactivated: {request.user.is_reactivated}")
            else:
                self.logger.debug("is_reactivated attribute not found")

            if not request.user.is_active and hasattr(request.user, 'is_reactivated') and not request.user.is_reactivated:
                self.logger.debug("User is blocked. Logging out...")
                logout(request)
                messages.error(request, "Your account has been blocked. Please contact support for assistance.")
                return HttpResponseRedirect(reverse('home'))
            elif request.user.is_active and request.user.is_reactivated:
                self.logger.debug("User has been reactivated by admin. Logging out...")
                logout(request)
                messages.error(request, "Your account has been reactivated. Please log in again.")
                return HttpResponseRedirect(reverse('accounts:login'))

        response = self.get_response(request)
        return response
