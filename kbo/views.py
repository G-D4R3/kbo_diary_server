from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.response import Response


# Create your views here.
class GameListAPIView(ListAPIView):
    serializer_class = None

    def list(self, request, *args, **kwargs):

        return Response()