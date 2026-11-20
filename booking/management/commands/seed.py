from django.core.management.base import BaseCommand
from booking.layouts import FIXTURES, GENERIC, GENERIC_FIXTURES, LAYOUTS
from booking.models import Restaurant, Table

DATA = {
    "Khloe Cafeteria + Cafe": (
        "khloe", 
        "Modern Filipino bistro", 
        "Fresh takes on Filipino comfort food.", 
        "P. Inocentes Street, Naval, Biliran", 
        "10:00 AM - 10:00 PM"
    ),
    "Golden Sun Restaurant": (
        "golden-sun", "Indoor family dining", 
        "A perfect place for family and friends.", 
        "Riverside Caray-Caray, Naval, Biliran", 
        "10:00 AM - 10:00 PM"
    ),
    "Lub Dub Cafe": (
        "lub-dub-cafe", 
        "Cafe and brunch", 
        "Coffee, pastries and all-day brunch.", 
        "Gov. Sabonsolin Road, Sitio Lupa, Brgy. Calumpang, Naval, Biliran", 
        "8:00 AM - 8:00 PM"
    ),
}


class Command(BaseCommand):
    help = "Create the 3 restaurants, mapped tables and demo accounts (safe to re-run; re-applies table layouts)."

    def handle(self, *a, **k):
        for name, (slug, cuisine, desc, loc, hours) in DATA.items():
            r, _ = Restaurant.objects.get_or_create(slug=slug, defaults=dict(name=name, cuisine=cuisine, description=desc))
            if slug in ("khloe", "golden-sun"):
                r.name = name
            r.fixtures = FIXTURES.get(slug, GENERIC_FIXTURES)
            if not r.location:
                r.location, r.hours = loc, hours
            if r.slug == "golden-sun":
                r.cuisine, r.description = cuisine, desc
            r.save()
            rows = LAYOUTS.get(slug, GENERIC)
            r.table_set.exclude(name__in=[x[0] for x in rows]).filter(reservation__isnull=True).delete()
            for tn, seats, shape, x, y in rows:
                Table.objects.update_or_create(restaurant=r, name=tn, defaults=dict(seats=seats, shape=shape, x=x, y=y))
        self.stdout.write(self.style.SUCCESS("Seeded restaurants and table layouts. No accounts were created."))
