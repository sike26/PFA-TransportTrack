import pandas as pd
import datetime
import networkx as nx
import os
import sys
import getopt
import gzip
import requests
import zipfile
import unicodedata
# from project.models import *


def is_int(s):
    try:
        int(s)
        return True
    except:
        return False



class GraphTBC(object):

    gtfs = []

    def __init__(self):

        path_learn_dirname = os.path.dirname(os.path.realpath(__file__))

# to comment
        # self.get_file(os.path.join(path_learn_dirname, "BUS/bus_gtfs"), 68, 14)
        # self.get_file(os.path.join(path_learn_dirname, "TRAM/tram_gtfs"), 67, 14)
        #
        # self.uncompress(os.path.join(path_learn_dirname, "BUS/bus_gtfs"), create_file=True, folder="BUS/")
        # self.uncompress(os.path.join(path_learn_dirname, "TRAM/tram_gtfs"), create_file=True, folder="TRAM/")
#

        self.bus_df_stops = pd.read_csv(os.path.join(path_learn_dirname, 'BUS/stops.txt'), encoding='utf-8')
        self.bus_df_routes = pd.read_csv(os.path.join(path_learn_dirname, 'BUS/routes.txt'), encoding='utf-8')
        self.bus_df_trips = pd.read_csv(os.path.join(path_learn_dirname, 'BUS/trips.txt'), encoding='utf-8')
        self.bus_df_stop_times = pd.read_csv(os.path.join(path_learn_dirname, 'BUS/stop_times.txt'), encoding='utf-8')

        self.tram_df_stops = pd.read_csv(os.path.join(path_learn_dirname, 'TRAM/stops.txt'), encoding='utf-8')
        self.tram_df_routes = pd.read_csv(os.path.join(path_learn_dirname, 'TRAM/routes.txt'), encoding='utf-8')
        self.tram_df_trips = pd.read_csv(os.path.join(path_learn_dirname, 'TRAM/trips.txt'), encoding='utf-8')
        self.tram_df_stop_times = pd.read_csv(os.path.join(path_learn_dirname, 'TRAM/stop_times.txt'), encoding='utf-8')

        self.tram_df_stops['stop_name'] = self.tram_df_stops['stop_name'].map(lambda s: unicodedata.normalize('NFD', s).encode('ascii', 'ignore').upper())
        self.bus_df_stops['stop_name'] = self.bus_df_stops['stop_name'].map(lambda s: unicodedata.normalize('NFD', s).encode('ascii', 'ignore').upper())

        self.tram_df_trips['trip_headsign'] = self.tram_df_trips['trip_headsign'].map(lambda s: unicodedata.normalize('NFD', s).encode('ascii', 'ignore').upper())
        self.bus_df_trips['trip_headsign'] = self.bus_df_trips['trip_headsign'].map(lambda s: unicodedata.normalize('NFD', s).encode('ascii', 'ignore').upper())


        self.bus_g = self._construct_graph(self.bus_df_stops, self.bus_df_routes, self.bus_df_trips, self.bus_df_stop_times)
        self.tram_g = self._construct_graph(self.tram_df_stops, self.tram_df_routes, self.tram_df_trips, self.tram_df_stop_times)

        self.g = nx.compose(self.bus_g, self.tram_g)

        self.dict_tram = self.get_paths_dict(transport_type="TRAM")
        self.dict_bus = self.get_paths_dict(transport_type="BUS")

        self.disturbed_stops = []

    def uncompress(self, filename, create_file=False, folder=""):

        path_learn_dirname = os.path.dirname(os.path.realpath(__file__))

        zfile = zipfile.ZipFile(filename, 'r')
        for zinfo in zfile.infolist():
            self.gtfs.append(zinfo.filename)

        if create_file:
            tag = 'wb'
        else:
            tag = 'a'

        for gtfs_file in self.gtfs:
            f = open(os.path.join(path_learn_dirname, folder+gtfs_file), tag)
            zdata = zfile.read(gtfs_file)
            f.write(zdata)
            f.close()

        zfile.close()


    def get_file(self, file_name, opt_gid, opt_format):

        parameters = {'gid' : opt_gid, 'format' : opt_format}
        r = requests.get('http://www.data.bordeaux-metropole.fr/files.php', params=parameters)

        with open(file_name, 'wb') as f :
            for chunk in r.iter_content(1000):
                f.write(chunk)


    def _construct_graph(self, df_stops, df_routes, df_trips, df_stop_times):

        df_trips = df_trips.drop_duplicates(["route_id", "direction_id", "trip_headsign"] )
        df_stop_times = df_stop_times[df_stop_times["trip_id"].isin(df_trips["trip_id"])]

        paths_dict = dict()
        for elt in df_trips["trip_id"]:
            df = df_stop_times[df_stop_times["trip_id"] == elt]
            paths_dict[elt] = df["stop_id"]

        g = nx.DiGraph()
        for elt in paths_dict:
            g.add_nodes_from(paths_dict[elt].tolist())
            g.add_edges_from(self.edges_build(paths_dict[elt].tolist()))

        return g


    def edges_build(self, stop_ids_list):
        l = len(stop_ids_list)-1
        i = 0
        edges_list = list()
        while (i<l):
            edges_list.append((stop_ids_list[i], stop_ids_list[i+1]))
            i = i+1
        return edges_list


    def route_id_to_name(self, route_id, transport_type="TRAM"):

        if transport_type == "TRAM":
            df_routes = self.tram_df_routes
        elif transport_type == "BUS":
            df_routes = self.bus_df_routes

        return df_routes[df_routes["route_id"] == route_id]["route_short_name"].tolist()[0]


    def stop_to_route(self, stop_name, transport_type="TRAM"):

        if transport_type == "TRAM":
            df_route = self.tram_df_routes
            df_stop_times = self.tram_df_stop_times
            df_trips = self.tram_df_trips
        elif transport_type == "BUS":
            df_route = self.bus_df_routes
            df_stop_times = self.bus_df_stop_times
            df_trips = self.bus_df_trips

        routes = []
        stop_ids = self.stop_name_to_id(stop_name, transport_type=transport_type)

        for sid in stop_ids:
            trip_id = df_stop_times[df_stop_times["stop_id"] == int(sid)]["trip_id"].tolist()[0]
            route_id = df_trips[df_trips["trip_id"] == trip_id]["route_id"].tolist()[0]
            routes.append(route_id)
        return list(set(map(lambda rid: self.route_id_to_name(rid, transport_type=transport_type), routes)))


    def stop_id_to_name(self, stop_id, transport_type="TRAM"):

        if transport_type == "TRAM":
            df_stops = self.tram_df_stops
        elif transport_type == "BUS":
             df_stops = self.bus_df_stops

        if (type(stop_id) == str):
            return df_stops[df_stops["stop_id"] == stop_id]["stop_name"].tolist()[0]
        return df_stops[df_stops["stop_id"] == str(stop_id)]["stop_name"].tolist()[0]


    def get_paths_dict(self, transport_type='TRAM'):

        if transport_type == "TRAM":
            df_route = self.tram_df_routes
            df_stop_times = self.tram_df_stop_times
            df_trips = self.tram_df_trips
        elif transport_type == "BUS":
            df_route = self.bus_df_routes
            df_stop_times = self.bus_df_stop_times
            df_trips = self.bus_df_trips

        df_trips = df_trips.drop_duplicates(["route_id", "direction_id", "trip_headsign"] )
        df_stop_times = df_stop_times[df_stop_times["trip_id"].isin(df_trips["trip_id"])]

        paths_dict = dict()
        keys_info = dict ()
        for elt in df_trips["trip_id"]:
            route = df_trips[df_trips["trip_id"] == elt]["route_id"].tolist()[0]
            direction = df_trips[df_trips["trip_id"] == elt]["direction_id"].tolist()[0]
            trip_headsign = df_trips[df_trips["trip_id"] == elt]["trip_headsign"].tolist()[0]
            info = [route, direction, trip_headsign]
            df = df_stop_times[df_stop_times["trip_id"] == elt]
            paths_dict[elt] = df["stop_id"].tolist()
            keys_info[elt] = info
        return paths_dict


    def interval_to_direction(self, start_stop, finish_stop, line, transport_type="TRAM"):

        start_stop_id_0 = this.stop_name_to_id(start_stop, transport_type=transport_type, direction=0)
        start_stop_id_1 = this.stop_name_to_id(start_stop, transport_type=transport_type, direction=1)

        finish_stop_id_0 = this.stop_name_to_id(finish_stop, transport_type=transport_type, direction=0)
        finish_stop_id_1 = this.stop_name_to_id(finish_stop, transport_type=transport_type, direction=1)

        if transport_type == 'TRAM':
            dict_ = self.dict_tram
        elif transport_type == 'BUS':
            dict_ = self.dict_bus

        if len(this.breakdown_affected_stops(dict_, start_stop_id_0, finish_stop_id_1)) > 2:
            return 1
        else:
            return 2


    def stop_name_to_id(self, stop_name, transport_type="TRAM", direction=None):

        if not direction in [None, 0, 1]:
            return []

        if transport_type == "TRAM":
            df_stops = self.tram_df_stops
            df_stop_times = self.tram_df_stop_times
            df_trips = self.tram_df_trips
        elif transport_type == "BUS":
            df_stops = self.bus_df_stops
            df_stop_times = self.bus_df_stop_times
            df_trips = self.bus_df_trips

        L = df_stops[df_stops["stop_name"] == stop_name]["stop_id"].tolist()
        L_int = []
        L_return = []


        for sid in L:
            if is_int(sid):
                L_int.append(int(sid))

        if not direction is None:
            for sid in L_int:

                trip_id_list = df_stop_times[df_stop_times["stop_id"] == sid]["trip_id"].tolist()
                for tid in trip_id_list:
                    if direction == 0:
                        if df_trips[df_trips["trip_id"] == tid]["direction_id"].tolist()[0] == 0:
                            return sid
                    else:
                        if df_trips[df_trips["trip_id"] == tid]["direction_id"].tolist()[0] == 1:
                            return sid

        return L_int


    def route_stops(self, route_id, direction, transport_type="TRAM"):
        if transport_type == "TRAM":
            df_stops = self.tram_df_stops
            df_stop_times = self.tram_df_stop_times
            df_trips = self.tram_df_trips
        elif transport_type == "BUS":
            df_stops = self.bus_df_stops
            df_stop_times = self.bus_df_stop_times
            df_trips = self.bus_df_trips

        tids = df_trips[df_trips["route_id"] == route_id][df_trips["direction_id"] == direction]["trip_id"]
        return sorted(list(set(df_stop_times[df_stop_times["trip_id"].isin(tids)]["stop_id"].tolist())))


    def get_route_direction(self, route_id, transport_type="TRAM"):
        if transport_type == "TRAM":
            df_trips = self.tram_df_trips
        elif transport_type == "BUS":
            df_trips = self.bus_df_trips

        return sorted(list(set(df_trips[df_trips["route_id"] == route_id]["trip_headsign"].tolist())))


    def belongs_to_dict (self, dict_, x):
        return_dict = dict()
        for key, list_ in dict_.items():
            if x in list_:
                #lists.append(list_)
                return_dict[key] = list_
        return return_dict


    def breakdown_affected_stops(self, dict_, stop_1, stop_2):
        affected_stops = set()
        affected_stops.add(stop_1)
        for key, list_ in dict_.items():
            if (stop_1 in list_) & (stop_2 in list_):
                index_1 = list_.index(stop_1)
                index_2 = list_.index(stop_2)
                for index, elt in enumerate(list_):
                    if ((index < index_2) & (index > index_1) | (index < index_1) & (index > index_2)):
                        affected_stops.add(elt)
        affected_stops.add(stop_2)
        return affected_stops


    def disturbance_affected_stops(self, disturbance):

        end_stops = []
        stops = map(lambda s: s.name, disturbance.stops.all())

        if disturbance.classType == "NONPERTINANT":
            return []

        if disturbance.line in [59, 60, 61]:
            transport_type = 'TRAM'
            paths_dict = self.dict_tram
        else:
            transport_type = 'BUS'
            paths_dict = self.dict_bus

        d = disturbance.direction
        L = []

        if len(stops) == 3:
            if d < 2:
                l1 = self.breakdown_affected_stops(paths_dict,
                                                self.stop_name_to_id(stops[0], transport_type=transport_type, direction=d),
                                                self.stop_name_to_id(stops[1], transport_type=transport_type, direction=d))
                l2 = self.breakdown_affected_stops(paths_dict,
                                                self.stop_name_to_id(stops[0], transport_type=transport_type, direction=d),
                                                self.stop_name_to_id(stops[2], transport_type=transport_type, direction=d))
                L = list(set(l1.extend(l2)))
                self.disturbed_stops.extend(L)
                return L
            else:
                l1 = self.breakdown_affected_stops(paths_dict,
                                                self.stop_name_to_id(stops[0], transport_type=transport_type, direction=0),
                                                self.stop_name_to_id(stops[1], transport_type=transport_type, direction=0))
                l2 = self.breakdown_affected_stops(paths_dict,
                                                self.stop_name_to_id(stops[0], transport_type=transport_type, direction=0),
                                                self.stop_name_to_id(stops[2], transport_type=transport_type, direction=0))
                L.extend(l1)
                L.extend(l2)

                l1 = self.breakdown_affected_stops(paths_dict,
                                                self.stop_name_to_id(stops[0], transport_type=transport_type, direction=1),
                                                self.stop_name_to_id(stops[1], transport_type=transport_type, direction=1))
                l2 = self.breakdown_affected_stops(paths_dict,
                                                self.stop_name_to_id(stops[0], transport_type=transport_type, direction=1),
                                                self.stop_name_to_id(stops[2], transport_type=transport_type, direction=1))
                L.extend(l1)
                L.extend(l2)
                L = list(set(L))
                self.disturbed_stops.extend(L)
                return L

        elif len(stops) == 2:
            if d < 2:
                L = self.route_stops(disturbance.line, d, transport_type=transport_type)
                self.disturbed_stops.extend(L)
                return L
            else:
                L.extend(self.breakdown_affected_stops(paths_dict,
                                                    self.stop_name_to_id(stops[0], transport_type=transport_type, direction=0),
                                                    self.stop_name_to_id(stops[1], transport_type=transport_type, direction=0)))
                L.extend(self.breakdown_affected_stops(paths_dict,
                                                    self.stop_name_to_id(stops[0], transport_type=transport_type, direction=1),
                                                    self.stop_name_to_id(stops[1], transport_type=transport_type, direction=1)))
                self.disturbed_stops.extend(L)
                return L

        elif len(stops) == 1:
            if d < 2:
                L = self.route_stops(disturbance.line, d, transport_type=transport_type)
                self.disturbed_stops.extend(L)
                return L
            else:
                for d in [0, 1]:
                    L.entend(self.route_stops(disturbance.line, d, transport_type=transport_type))

                self.disturbed_stops.extend(L)
                return L

        else:
            return []


    def line_transport_type(self, route_id):
        if route_id in [59, 60, 61]:
            return "TRAM"
        else:
            return "BUS"


    def is_path_disturb(self, path):

        subpaths = path.subpaths

        # get the direction
        for sp in subpaths:
            tt = self.line_transport_type(line)
            d = interval_to_direction(sp.transportStopStart, sp.transportStopFinish, line, transport_type=tt)

            stops = self.breakdown_affected_stops(paths_dict,
                                                  self.stop_name_to_id(sp.transportStopStart, transport_type=tt, direction=d),
                                                  self.stop_name_to_id(sp.transportStopFinish, transport_type=tt, direction=d))

            affected_stops = [s for s in stops if s in self.disturbed_stops]

            if len(affected_stops) == 0:
                return False
            else:
                return True
