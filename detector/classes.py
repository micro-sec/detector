class Agent:
    def __init__(self, name, ip_address):
        self.name = name
        self.ip_address = ip_address
        self.ws_port = None
        self.ws_max_size = None
        self.syscalls_compression = None
        self.ws_client_thread = None
        self.ids_config = list()

    def stop_monitoring(self):
        if self.ws_client_thread is not None:
            self.ws_client_thread.terminate()
            self.ws_client_thread = None
        for i in self.ids_config:
            i.stop_inspecting()
        self.ids_config.clear()

    def stop_inspecting(self, identifier=None):
        if identifier is None:
            for i in self.ids_config:
                i.stop_inspecting()
            self.ids_config.clear()
        else:
            for i in self.ids_config:
                if identifier == i.identifier:
                    i.stop_inspecting()
                    self.ids_config.remove(i)
                    break


class IntrusionDetectionConfig:
    def __init__(self, identifier, detection_type, algorithm, duration, start_time, start_time_timestamp,
                 ids_process, duration_thread):
        self.identifier = identifier
        self.detection_type = detection_type
        self.algorithm = algorithm
        self.duration = duration
        self.start_time = start_time
        self.start_time_timestamp = start_time_timestamp
        self.ids_process = ids_process
        self.duration_thread = duration_thread

    def stop_inspecting(self):
        if self.ids_process is not None:
            self.ids_process.kill()
        if self.duration_thread is not None:
            self.duration_thread.terminate()
