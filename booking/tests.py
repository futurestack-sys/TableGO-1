from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Reservation, Restaurant, RestaurantManager, Table


class HomeRoleAccessTests(TestCase):
    def test_admin_and_manager_are_redirected_to_dashboard(self):
        admin = User.objects.create_superuser(username="admin", password="test-pass")
        manager = User.objects.create_user(username="manager", password="test-pass")
        restaurant = Restaurant.objects.create(name="Test Restaurant", slug="test-restaurant", cuisine="Test")
        RestaurantManager.objects.create(user=manager, restaurant=restaurant)

        for account in (admin, manager):
            with self.subTest(account=account.username):
                self.client.force_login(account)
                response = self.client.get(reverse("home"))
                self.assertRedirects(response, reverse("dashboard"))

    def test_admin_can_explicitly_browse_home(self):
        admin = User.objects.create_superuser(username="admin", password="test-pass")
        self.client.force_login(admin)

        response = self.client.get(reverse("home"), {"browse": "1"})

        self.assertEqual(response.status_code, 200)

    def test_customer_can_access_home(self):
        customer = User.objects.create_user(username="customer", password="test-pass")
        self.client.force_login(customer)

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)


class AccountManagementTests(TestCase):
    def test_accounts_are_grouped_by_role(self):
        admin = User.objects.create_superuser(username="admin", password="test-pass")
        manager = User.objects.create_user(username="manager", password="test-pass")
        customer = User.objects.create_user(username="customer", password="test-pass")
        restaurant = Restaurant.objects.create(name="Test Restaurant", slug="test-restaurant", cuisine="Test")
        RestaurantManager.objects.create(user=manager, restaurant=restaurant)
        self.client.force_login(admin)

        response = self.client.get(reverse("d_customers"))

        self.assertEqual(response.status_code, 200)
        groups = {group["slug"]: list(group["users"]) for group in response.context["role_groups"]}
        self.assertEqual(groups["administrators"], [admin])
        self.assertEqual(groups["managers"], [manager])
        self.assertEqual(groups["customers"], [customer])
        self.assertContains(response, "Account Management")
        self.assertContains(response, "Administrators")
        self.assertContains(response, "Restaurant managers")
        self.assertContains(response, "Customers")
        self.assertNotContains(response, "Customer Management")


class ReservationCustomerNameTests(TestCase):
    def test_customer_name_is_saved_when_reservation_is_confirmed(self):
        customer = User.objects.create_user(username="booking_customer", password="test-pass")
        restaurant = Restaurant.objects.create(name="Test Restaurant", slug="test-restaurant", cuisine="Test")
        table = Table.objects.create(restaurant=restaurant, name="T1", seats=4)
        self.client.force_login(customer)

        url = reverse("restaurant", args=[restaurant.slug])
        details = {
            "customer_name": "Test Guest",
            "date": (timezone.localdate() + timedelta(days=1)).isoformat(),
            "time": "18:00",
            "guests": "2",
        }
        response = self.client.post(url, details)
        self.assertContains(response, "Table Selection")

        response = self.client.get(url, {**{key: value for key, value in details.items() if key != "customer_name"}, "table": table.pk})
        self.assertContains(response, "Test Guest")
        self.assertNotIn("customer_name", response.wsgi_request.GET)

        response = self.client.post(url, {
            "confirm": "1",
            "date": details["date"],
            "time": details["time"],
            "guests": details["guests"],
            "table": str(table.pk),
        })

        self.assertRedirects(response, reverse("my"))
        reservation = Reservation.objects.get(customer=customer, restaurant=restaurant)
        self.assertEqual(reservation.customer_name, "Test Guest")