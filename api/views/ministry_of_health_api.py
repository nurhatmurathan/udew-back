import requests
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class DataSetOfInsuranceCards(APIView):

    def get(self, request, *args, **kwargs):
        iin = kwargs.get('iin')

        url = settings.MINISTRY_OF_HEALTH_DATASET_URL if not iin \
            else f"{settings.MINISTRY_OF_HEALTH_DATASET_URL}/{iin}/"

        headers = self._get_headers()
        return self._make_request(url, headers=headers)

    def _get_headers(self):
        return {'Authorization': f'Bearer {settings.MINISTRY_OF_HEALTH_DATASET_API_KEY}'}

    def _make_request(self, url, headers):
        global response

        try:

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            return Response(response.json())
        except requests.exceptions.HTTPError as e:
            return Response({'message': 'External API error', 'details': str(e)},
                            status=response.status_code)
        except requests.exceptions.RequestException as e:
            return Response({'message': 'Request failed', 'details': str(e)},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)
