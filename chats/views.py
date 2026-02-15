from django.shortcuts import render
from django.http import JsonResponse


def username_reveal(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error":"not authenticated"})

    return JsonResponse({"username": f"{request.user.username}"})