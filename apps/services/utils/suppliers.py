""" В этом файле находятся функции с поставщиками """

import xml.etree.ElementTree as ET
from django.db import transaction
from apps.suppliers.models import Supplier, City


def extract_suppliers_and_cities(xml_string):
    supplier_city_map = {}  # Dictionary to hold supplier and city pairs

    # Parse the XML string
    root = ET.fromstring(xml_string)

    # Find all supplier elements
    for supplier in root.findall('.//supplier'):
        title = supplier.get('supplierTitle')
        city = supplier.get('city')

        if title and city:  # Check that values are not empty
            supplier_city_map[title] = city  # Map supplier to city

    return supplier_city_map


def save_suppliers_and_cities(supplier_city_map):
    # Create a set to hold existing city names for efficiency
    existing_cities = set(City.objects.values_list('name', flat=True))

    # Create or update cities
    for city_name in supplier_city_map.values():
        if city_name not in existing_cities:
            city = City(name=city_name)
            city.save()

    # Create or update suppliers
    for supplier_name, city_name in supplier_city_map.items():
        # Get the city object, assuming it exists now
        city = City.objects.get(name=city_name)

        # Create or update the supplier
        Supplier.objects.update_or_create(
            name=supplier_name,
            defaults={
                'article_number': None,  # or some default value
                'priority': 1,           # default priority
                'visual_priority': 3,     # default visual priority
                'city': city              # Associate the supplier with the city object
            }
        )