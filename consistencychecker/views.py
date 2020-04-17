# Create your views here.
from django.views import View


class LoadConsistencyHTML(View):
    """ load  web page to load files """

    def get(self, request):
        template = 'datamanager/loadManager.html'

        # define the order table appear in web page
        tables = [
            {
                'bubble_title': '', 'bubble_content': 'Archivo de perfiles de carga',
                'id': 'profileTable', 'title_icon': 'fa-bus', 'title': 'Perfiles'
            },
            {
                'bubble_title': '', 'bubble_content': 'Archivos de velocidades',
                'id': 'speedTable', 'title_icon': 'fa-tachometer', 'title': 'Velocidades'
            },
            {
                'bubble_title': '', 'bubble_content': 'Información de las etapas hechas por usuario en cada servicio.',
                'id': 'odbyrouteTable', 'title_icon': 'fa-map-o', 'title': 'etapas por servicio'
            },
            {
                'bubble_title': '', 'bubble_content': 'Datos de la ejecución de adatrap',
                'id': 'generalTable', 'title_icon': 'fa-clone', 'title': 'Datos generales'
            },
            {
                'bubble_title': '', 'bubble_content': 'Datos de la distribución de validaciones en zonas pago',
                'id': 'paymentfactorTable', 'title_icon': 'fa-money',
                'title': 'Distribución de validaciones en zona de pago'
            },
            {
                'bubble_title': '', 'bubble_content': 'Archivos de viajes',
                'id': 'tripTable', 'title_icon': 'fa-line-chart', 'title': 'Viajes'
            },
            {
                'bubble_title': '', 'bubble_content': 'Archivos de validaciones bip',
                'id': 'bipTable', 'title_icon': 'fa-line-chart', 'title': 'Validaciones Bip'
            }
        ]
        operation_program_tables = [
            {
                'bubble_title': '', 'bubble_content': 'Archivo con geometría de servicios',
                'id': 'shapeTable', 'title_icon': 'fa-code-fork', 'title': 'Geometria de servicios'
            },
            {
                'bubble_title': '', 'bubble_content': 'Archivo con secuencia de paradas por servicio',
                'id': 'stopTable', 'title_icon': 'fa-map-marker', 'title': 'Secuencia de paradas'
            }
        ]
        context = {
            'tables': tables,
            'operation_program_tables': operation_program_tables
        }

        return render(request, template, context)
