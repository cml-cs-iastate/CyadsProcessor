import serpy


class LocationSerializer(serpy.Serializer):
    state_name = serpy.StrField()
    state_symbol = serpy.StrField()


class BatchSerializer(serpy.Serializer):
    id = serpy.Field()
    location = LocationSerializer()
    start_datetime = serpy.Field()
    completed_datetime = serpy.Field()

    start_timestamp = serpy.IntField()
    completed_timestamp = serpy.IntField()
    time_taken = serpy.IntField()
    total_bots = serpy.IntField()
    external_ip = serpy.StrField()
    status = serpy.StrField()
    video_list_size = serpy.IntField()
    server_hostname = serpy.StrField()
    server_container = serpy.StrField()
    synced = serpy.BoolField()
    processed = serpy.BoolField()
