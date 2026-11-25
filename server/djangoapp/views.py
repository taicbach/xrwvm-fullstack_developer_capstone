# Uncomment the required imports before adding the code

# from django.shortcuts import render
# from django.http import HttpResponseRedirect, HttpResponse
# from django.contrib.auth.models import User
# from django.shortcuts import get_object_or_404, render, redirect
# from django.contrib.auth import logout
# from django.contrib import messages
# from datetime import datetime

from .restapis import get_request, analyze_review_sentiments, post_review
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
# from .populate import initiate


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

# Create a `logout_request` view to handle sign out request
# def logout_request(request):
# ...

# Create a `registration` view to handle sign up request
# @csrf_exempt
# def registration(request):
# ...

# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
# def get_dealerships(request):
# ...

# Create a `get_dealer_reviews` view to render the reviews of a dealer
# def get_dealer_reviews(request,dealer_id):
# ...

# Create a `get_dealer_details` view to render the dealer details
# def get_dealer_details(request, dealer_id):
# ...

# Create a `add_review` view to submit a review
# def add_review(request):
# ...

# Get all dealerships or dealerships from one state
def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state

    dealerships = get_request(endpoint)

    if dealerships is None:
        return JsonResponse({
            "status": 502,
            "message": "Unable to fetch dealerships"
        }, status=502)

    return JsonResponse({
        "status": 200,
        "dealers": dealerships
    })


# Get details for one dealership
def get_dealer_details(request, dealer_id):
    dealer = get_request("/fetchDealer/" + str(dealer_id))

    if dealer is None:
        return JsonResponse({
            "status": 502,
            "message": "Unable to fetch dealer"
        }, status=502)

    return JsonResponse({
        "status": 200,
        "dealer": dealer
    })


# Get reviews and analyze their sentiments
def get_dealer_reviews(request, dealer_id):
    reviews = get_request(
        "/fetchReviews/dealer/" + str(dealer_id)
    )

    if reviews is None:
        return JsonResponse({
            "status": 502,
            "message": "Unable to fetch reviews"
        }, status=502)

    for review in reviews:
        review_text = review.get("review", "")

        sentiment_result = analyze_review_sentiments(
            review_text
        )

        if isinstance(sentiment_result, dict):
            review["sentiment"] = sentiment_result.get(
                "sentiment", "neutral"
            )
        else:
            review["sentiment"] = "neutral"

    return JsonResponse({
        "status": 200,
        "reviews": reviews
    })


# Allow authenticated users to submit reviews
@csrf_exempt
def add_review(request):
    if request.user.is_anonymous:
        return JsonResponse({
            "status": 403,
            "message": "Unauthorized"
        }, status=403)

    if request.method != "POST":
        return JsonResponse({
            "status": 405,
            "message": "POST method required"
        }, status=405)

    try:
        data = json.loads(request.body)
    except (ValueError, TypeError):
        return JsonResponse({
            "status": 400,
            "message": "Invalid JSON"
        }, status=400)

    response = post_review(data)

    if response is None:
        return JsonResponse({
            "status": 502,
            "message": "Error posting review"
        }, status=502)

    return JsonResponse({
        "status": 200,
        "message": "Review posted successfully"
    })
