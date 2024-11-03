from asgiref.sync import sync_to_async

from apps.suppliers.models import Tire, TireSupplier, TruckTire, TruckTireSupplier, SpecialTire, SpecialTireSupplier, \
    MotoTire, MotoTireSupplier, Disk, DiskSupplier, TruckDisk, TruckDiskSupplier


@sync_to_async
def get_tire_objects(**tire_data):
    return Tire.objects.get_or_create(**tire_data)


@sync_to_async
def get_truck_objects(**truck_data):
    return TruckTire.objects.get_or_create(**truck_data)


@sync_to_async
def get_special_tire_objects(**special_tire_data):
    return SpecialTire.objects.get_or_create(**special_tire_data)


@sync_to_async
def get_moto_tire_objects(**moto_tire_data):
    return MotoTire.objects.get_or_create(**moto_tire_data)


@sync_to_async
def get_disk_elements_objects(**disk_elements_data):
    return Disk.objects.get_or_create(**disk_elements_data)


@sync_to_async
def get_trucks_disks_objects(**trucks_disks_data):
    return TruckDisk.objects.get_or_create(trucks_disks_data)


@sync_to_async
def tire_supplier_bulk_create(tire_data):
    TireSupplier.objects.bulk_create(tire_data)


@sync_to_async
def truck_tire_supplier_bulk_create(tire_data):
    TruckTireSupplier.objects.bulk_create(tire_data)


@sync_to_async
def special_tire_supplier_bulk_create(special_tire_data):
    return SpecialTireSupplier.objects.bulk_create(special_tire_data)


@sync_to_async
def moto_tire_supplier_bulk_create(moto_tire_data):
 MotoTireSupplier.objects.bulk_create(moto_tire_data)


@sync_to_async
def disk_supplier_bulk_create(disk_elements_data):
    DiskSupplier.objects.bulk_create(disk_elements_data)


@sync_to_async
def trucks_disks_supplier_bulk_create(trucks_disks_data):
    TruckDiskSupplier.objects.bulk_create(trucks_disks_data)
