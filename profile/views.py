from django.shortcuts import render
from django.views.generic import View

from localinfo.helper import get_halfhour_list_for_select_input, get_timeperiod_list_for_select_input, \
    get_day_type_list_for_select_input


class LoadProfileByExpeditionHTML(View):

    def get(self, request):
        template = "profile/byExpedition.html"

        indicator_table = '''
        <div class="row">
            <div class="col-md-4 col-md-offset-4">
                <table id="{0}" class="table table-striped table-bordered dt-responsive table-condensed nowrap">
                    <thead>
                        <tr>
                            <th class="text-center">N° de expediciones</th>
                            <th class="text-center">% de estimación de bajada</th>
                            <th class="text-center">CU del perfil con evasión (pax-km/plazas-km)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="text-center"><strong id='expeditionNumber'>-</strong></td>
                            <td class="text-center"><strong id='boardingWithAlightingPercentage'>-</strong></td>
                            <td class="text-center"><strong id='utilizationCoefficient'>-</strong></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        '''

        context = {
            'data_filter': {
                'minutes': get_halfhour_list_for_select_input(),
                'day_types': get_day_type_list_for_select_input(),

            },
            'tabs': {
                'header': ['Gráfico', 'Mapa'],
                'content': [indicator_table + '<div id="barChart" style="height:600px;"></div>',
                            '<div id="mapid" style="height: 500px;min-height: 500px"></div>']
            }
        }

        return render(request, template, context)


class LoadProfileByStopHTML(View):

    def get(self, request):
        template = "profile/byStop.html"

        context = {
            'data_filter': {
                'minutes': get_halfhour_list_for_select_input(),
                'day_types': get_day_type_list_for_select_input()
            }
        }

        return render(request, template, context)


class ODMatrixHTML(View):

    def get(self, request):
        template = "profile/odmatrix.html"

        context = {
            'data_filter': {
                'minutes': get_halfhour_list_for_select_input(),
                'day_types': get_day_type_list_for_select_input()
            }
        }

        return render(request, template, context)


class TrajectoryHTML(View):

    def get(self, request):
        template = "profile/trajectory.html"

        context = {
            'data_filter': {
                'minutes': get_halfhour_list_for_select_input(),
                'day_types': get_day_type_list_for_select_input()
            }
        }

        return render(request, template, context)


class TransfersView(View):

    def get(self, request):
        template = "profile/transfers.html"

        context = {
            'data_filter': {
                'minutes': get_halfhour_list_for_select_input(),
                'day_types': get_day_type_list_for_select_input()
            }
        }

        return render(request, template, context)


class LoadProfileByManyStopsHTML(View):

    def get(self, request):
        template = "profile/byManyStops.html"

        context = {
            'data_filter': {
                'minutes': get_halfhour_list_for_select_input(),
                'day_types': get_day_type_list_for_select_input()
            }
        }

        return render(request, template, context)
