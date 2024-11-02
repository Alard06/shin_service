def process_truck_disks(root, truck_disks, company_id):
    trucks = ET.SubElement(root, 'truckDisks')
    for truck_disk_id, data in truck_disks.items():
        truck_disk_element = ET.SubElement(trucks, "truckDisk",
                                           id=truck_disk_id,
                                           brandArticul=str(data['product'].brand_articul) if data[
                                               'product'].brand_articul else '',
                                           brand=data['product'].brand,
                                           product=data['product'].product,
                                           fullTitle=data['product'].full_title,
                                           headline='#',
                                           measurement=get_measurement(data['product'].width),
                                           recommendedPrice='',
                                           model=data['product'].model,
                                           width=data['product'].width,
                                           height='',
                                           diameter=data['product'].diameter,
                                           season='',
                                           spike="",
                                           lightduty='',
                                           indexes='',
                                           system='',
                                           omolagation='',
                                           mud='',
                                           at='',
                                           runFlatTitle='',
                                           fr='',
                                           xl='',
                                           autobrand='',
                                           pcd=str(data['product'].pcd if data['product'].pcd else ''),
                                           boltcount=str(
                                               data['product'].boltcount if data['product'].boltcount else ''),
                                           drill='',
                                           outfit='',
                                           dia=str(data['product'].dia if data['product'].dia else ''),
                                           color=str(data['product'].color if data['product'].color else ''),
                                           type=str(data['product'].type if data['product'].type else ''),
                                           numberOfPlies='',
                                           axis='',
                                           quadro='',
                                           special='',
                                           note='',
                                           typesize='',
                                           kit='',
                                           layers='',
                                           camera='',
                                           Dioganal='',
                                           Solid='',
                                           Note=str(data['product'].note) if data[
                                               'product'].note else '',
                                           Countries='',
                                           runflat='',
                                           ProtectorType='',
                                           )

        sorted_suppliers = sort_suppliers(data['suppliers'], company_id)

        articuls, best_supplier, best_price, total_quantity, best_delivery_period_days, product_supplier = process_suppliers(
            sorted_suppliers, data['product'], company_id, is_truck_disks=True)

        if best_supplier:
            create_supplier_element(truck_disk_element, articuls, best_supplier, best_price, total_quantity,
                                    best_delivery_period_days, product_supplier, is_truck_tire=True)