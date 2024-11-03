async def tires_elements(suppliers, cities, file_path):
    print('tires_elements')
    tire_suppliers_to_create = []
    tire_objects = {}

    # Use lxml for faster parsing
    for event, elem in etree.iterparse(file_path, events=('end',), tag='tire'):
        tire_data = {
            'id_tire': elem.get('id'),
            'brand': elem.get('brand'),
            'brand_article': elem.get('brandArticul'),
            'product': elem.get('product'),
            'image': elem.get('image'),
            'full_title': elem.get('fullTitle'),
            'model': elem.get('model'),
            'season': elem.get('season'),
            'spike': elem.get('spike') == 'да',
            'runflat': elem.get('runflat') == 'да',
            'lightduty': elem.get('lightduty') == 'да',
            'indexes': elem.get('indexes'),
            'width': elem.get('width'),
            'height': elem.get('height'),
            'diameter': elem.get('diameter'),
            'system': elem.get('system'),
            'omolagation': elem.get('omolagation'),
            'mud': elem.get('mud'),
            'at': elem.get('at'),
            'runFlatTitle': elem.get('runFlatTitle'),
            'fr': elem.get('fr'),
            'xl': elem.get('xl')
        }

        tire_obj = tire_objects.get(tire_data['full_title'])
        if tire_obj is None:
            tire_obj, created = await get_tire_objects(**tire_data)
            tire_objects[tire_data['full_title']] = tire_obj
        for supplier in elem.findall('supplier'):
            articul = supplier.get('articul')
            price = supplier.get('price')
            input_price = supplier.get('inputPrice')
            quantity = supplier.get('quantity')
            supplier_title = supplier.get('supplierTitle')
            city_name = supplier.get('city')
            presence = supplier.get('presence')
            delivery_period_days = supplier.get('deliveryPeriodDays')
            last_availability_date = supplier.get('lastAvailabilityDate')
            sale = supplier.get('sale') == 'yes'

            if last_availability_date:
                last_availability_date_aware = timezone.make_aware(
                    timezone.datetime.strptime(last_availability_date, '%d.%m.%Y %H:%M:%S')
                )
            else:
                last_availability_date_aware = None

            supplier_obj = suppliers.get(supplier_title)
            city_obj = cities.get(city_name)

            if supplier_obj and city_obj:
                tire_suppliers_to_create.append(
                    TireSupplier(
                        tire=tire_obj,
                        articul=articul,
                        price=price,
                        input_price=input_price,
                        quantity=quantity,
                        supplier=supplier_obj,
                        city=city_obj,
                        presence=presence,
                        delivery_period_days=delivery_period_days,
                        last_availability_date=last_availability_date_aware,
                        sale=sale
                    )
                )
        elem.clear()  # Clear the element to free memory
        if len(tire_suppliers_to_create) >= 50:
            try:
                await tire_supplier_bulk_create(tire_suppliers_to_create)
                tire_suppliers_to_create.clear()  # Clear the list after bulk insert
            except Exception as e:
                print(f"Error during bulk_create: {e}")
                print('created tire')

    if tire_suppliers_to_create:
        try:

            await tire_supplier_bulk_create(tire_suppliers_to_create)
            print('created tire_supplier_bulk_create')
        except Exception as e:
            print(f"Error during final bulk_create: {e}")

    print('TIRE OK')