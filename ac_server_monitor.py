
import codecs
import socket
import struct
import sys
from data_persistence import Database
from data_schemas import GameSession, ClientSession, Lap
import proto
SUPPORTED_PROTOCOLS = [2, 4]
import time

class Vector3f(object):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0

    def __str__(self):
        return '[%f, %f, %f]' % (self.x, self.y, self.z)

class BinaryReader(object):
    def __init__(self, data):
        self.data = data
        self.offset = 0

    def read_byte(self):
        fmt = 'B'
        r = struct.unpack_from(fmt, self.data, self.offset)[0]
        self.offset += struct.calcsize(fmt)
        return r

    def read_bytes(self, length):
        fmt = '%dB' % length
        r = struct.unpack_from(fmt, self.data, self.offset)
        self.offset += struct.calcsize(fmt)
        return r

    def read_int32(self):
        fmt = 'i'
        r = struct.unpack_from(fmt, self.data, self.offset)[0]
        self.offset += struct.calcsize(fmt)
        return r

    def read_single(self):
        fmt = 'f'
        r = struct.unpack_from(fmt, self.data, self.offset)[0]
        self.offset += struct.calcsize(fmt)
        return r

    def read_string(self):
        length = self.read_byte()
        bytes_str = self.read_bytes(length)
        return ''.join([chr(x) for x in bytes_str])

    def read_uint16(self):
        fmt = 'H'
        r = struct.unpack_from(fmt, self.data, self.offset)[0]
        self.offset += struct.calcsize(fmt)
        return r

    def read_uint32(self):
        fmt = 'I'
        r = struct.unpack_from(fmt, self.data, self.offset)[0]
        self.offset += struct.calcsize(fmt)
        return r

    def read_utf_string(self):
        length = self.read_byte()
        bytes_str = self.read_bytes(length * 4)

        return bytes(bytes_str).decode('utf-32')

    def read_vector_3f(self):
        v = Vector3f()
        v.x = self.read_single()
        v.y = self.read_single()
        v.z = self.read_single()

        return v


class BinaryWriter(object):
    def __init__(self):
        self.buff = b''

    def write_byte(self, data):
        self.buff += struct.pack('B', data)

    def write_bytes(self, data, length):
        self.buff += struct.pack('%dB' % length, *data)

    def write_uint16(self, data):
        self.buff += struct.pack('H', data)

    def write_utf_string(self, data):
        self.write_byte(len(data))

        bytes_str = data.encode('utf-32')
        if bytes_str.startswith(codecs.BOM_UTF32):
            # Remove the BOM
            bytes_str = bytes_str[len(codecs.BOM_UTF32):]
        self.write_bytes(bytes_str, len(bytes_str))


class ServerMonitor(object):
    def __init__(self):
        self.br = None
        self.db = Database()
    def _check_protocol(self, protocol_version):
        '''
        Checks that the given procotol version is supported,
        the program will quit otherwise
        '''
        if protocol_version not in SUPPORTED_PROTOCOLS:
            print('Unsupported protocol version: %d, expecting: %s' %
                  (protocol_version, SUPPORTED_PROTOCOLS))
            sys.exit(1)

    def _handle_car_info(self):
        car_id = self.br.read_byte()
        is_connected = self.br.read_byte() != 0
        car_model = self.br.read_utf_string()
        car_skin = self.br.read_utf_string()
        driver_name = self.br.read_utf_string()
        driver_team = self.br.read_utf_string()
        driver_guid = self.br.read_utf_string()
        # TODO: implement example testSetSessionInfo()

    def _handle_car_update(self):
        car_id = self.br.read_byte()
        pos = self.br.read_vector_3f()
        velocity = self.br.read_vector_3f()
        gear = self.br.read_byte()
        engine_rpm = self.br.read_uint16()
        normalized_spline_pos = self.br.read_single()

    def _handle_chat(self):
        car_id = self.br.read_byte()
        msg = self.br.read_utf_string()

    def _handle_client_event(self):
        event_type = self.br.read_byte()
        car_id = self.br.read_byte()
        other_car_id = 255

        if event_type == proto.ACSP_CE_COLLISION_WITH_CAR:
            other_car_id = self.br.read_byte()
        elif event_type == proto.ACSP_CE_COLLISION_WITH_ENV:
            pass

        impact_speed = self.br.read_single()
        world_pos = self.br.read_vector_3f()
        rel_pos = self.br.read_vector_3f()

    def _handle_client_loaded(self):
        car_id = self.br.read_byte()

    def _handle_connection_closed(self):
        driver_name = self.br.read_utf_string()
        driver_guid = self.br.read_utf_string()
        self.db.saveClientDisconnection(driver_guid)

    def _handle_end_session(self):
        filename = self.br.read_utf_string()
        print('====')
        print('Report JSON available at: %s' % filename)

    def _handle_error(self):
        print('====')
        print('ERROR: %s' % self.br.read_utf_string())

    def _handle_lap_completed(self):
        lap = Lap( 
                    car_number = self.br.read_byte(),
                    laptime = self.br.read_uint32(),
                    cuts = self.br.read_byte())
        cars_count = self.br.read_byte()
        for i in range(1, cars_count + 1):
            rcar_id = self.br.read_byte()
            rtime = self.br.read_uint32()
            rlaps = self.br.read_byte()
        lap.grip_level = self.br.read_byte()
        self.db.saveLap(lap)

    def _handle_new_connection(self):
        clientSession = ClientSession(
        driver_id = self.br.read_utf_string(),
        driver_guid = self.br.read_utf_string(),
        car_number = int(self.br.read_byte()),
        car_model = self.br.read_string(),
        skin = self.br.read_string(),
        )
        self.db.saveClientConnection(clientSession)

    def _handle_new_session(self):

        protocol_version = self.br.read_byte()
        sessionInfo = GameSession(
        session_index = self.br.read_byte(),
        current_session_index = self.br.read_byte(),
        session_count = self.br.read_byte(),
        server_name = self.br.read_utf_string(),
        track_name = self.br.read_string(),
        track_config = self.br.read_string(),
        session_name = self.br.read_string(),
        session_type = self.br.read_byte(),
        session_time = self.br.read_uint16(),
        lap_number = self.br.read_uint16(),
        wait_time = self.br.read_uint16(),
        ambient_temp = self.br.read_byte(),
        road_temp = self.br.read_byte(),
        weather_graphics = self.br.read_string(),
        elapsed_ms = self.br.read_int32())
   
        if(sessionInfo.elapsed_ms == 0):
            self.db.saveNewGameSession(sessionInfo)

    def _handle_session_info(self):
        protocol_version = self.br.read_byte()
        sessionInfo = GameSession(
        session_index = self.br.read_byte(),
        current_session_index = self.br.read_byte(),
        session_count = self.br.read_byte(),
        server_name = self.br.read_utf_string(),
        track_name = self.br.read_string(),
        track_config = self.br.read_string(),
        session_name = self.br.read_string(),
        session_type = self.br.read_byte(),
        session_time = self.br.read_uint16(),
        lap_number = self.br.read_uint16(),
        wait_time = self.br.read_uint16(),
        ambient_temp = self.br.read_byte(),
        road_temp = self.br.read_byte(),
        weather_graphics = self.br.read_string(),
        elapsed_ms = self.br.read_int32())
     
        self.db.updateGameSession(sessionInfo)

        print('====')
        print('Session Info')

    def _handle_version(self):
        protocol_version = self.br.read_byte()
        self._check_protocol(protocol_version)

    # The methods below are to send data to the server

    def run(self,sock):

        while True:
            sdata, _addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            self.br = BinaryReader(sdata)
            packet_id = self.br.read_byte()

            if packet_id == proto.ACSP_ERROR:
                self._handle_error()
            elif packet_id == proto.ACSP_CHAT:
                self._handle_chat()
            elif packet_id == proto.ACSP_CLIENT_LOADED:
                self._handle_client_loaded()

            elif packet_id == proto.ACSP_VERSION:
                self._handle_version()
            elif packet_id == proto.ACSP_NEW_SESSION:
                self._handle_new_session()

                # Uncomment to enable realtime position reports
                # self._enable_realtime_report()
            elif packet_id == proto.ACSP_SESSION_INFO:
                self._handle_session_info()
            elif packet_id == proto.ACSP_END_SESSION:
                self._handle_end_session()
            elif packet_id == proto.ACSP_CLIENT_EVENT:
                self._handle_client_event()
            elif packet_id == proto.ACSP_CAR_INFO:
                self._handle_car_info()
            elif packet_id == proto.ACSP_CAR_UPDATE:
                self._handle_car_update()
            elif packet_id == proto.ACSP_NEW_CONNECTION:
                self._handle_new_connection()
            elif packet_id == proto.ACSP_CONNECTION_CLOSED:
                self._handle_connection_closed()
            elif packet_id == proto.ACSP_LAP_COMPLETED:
                self._handle_lap_completed()
            else:
                print('** UNKOWNN PACKET ID: %d' % packet_id) 
            time.sleep(0.5)


