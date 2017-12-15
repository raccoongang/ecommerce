"""
Tests for management command for creating Sites, SiteThemes, SiteConfigurations and Partners.
"""
import logging
import os

from django.contrib.sites.models import Site
from django.core.management import CommandError, call_command
from django.test import TestCase
from oscar.core.loading import get_model

from ecommerce.core.models import SiteConfiguration
from ecommerce.theming.models import SiteTheme

logger = logging.getLogger(__name__)
Partner = get_model('partner', 'Partner')
SITES = ["dummy"]


class TestCreateSitesAndPartners(TestCase):
    """
    Test django management command for creating Sites, SiteThemes, SiteConfigurations and Partners.
    """

    def setUp(self):
        super(TestCreateSitesAndPartners, self).setUp()
        self.dns_name = "dummy-dns"
        self.theme_path = os.path.dirname(__file__)

    def _assert_site_and_partner_are_valid(self):
        """
        checks that all the sites and partners are valid.
        """
        sites = Site.objects.all()
        partners = Partner.objects.all()

        # there is an extra default site.
        self.assertEqual(len(sites), len(SITES) + 1)
        self.assertEqual(len(partners), len(SITES))

        for site in sites:
            if site.name in SITES:
                site_name = site.name
                self.assertEqual(
                    site.domain,
                    "discovery-{site}-{dns_name}.example.com".format(site=site_name, dns_name=self.dns_name)
                )
                partner = Partner.objects.get(site=site)

                self.assertEqual(partner.short_code, site_name)
                self.assertEqual(partner.name, "dummy")
                self.assertEqual(partner.oidc_key, "key-dummy")
                self.assertEqual(partner.oidc_secret, "secret-{dns_name}".format(dns_name=self.dns_name))
                self.assertEqual(
                    partner.oidc_url_root,
                    "https://dummy-{dns_name}.example.com/oauth2".format(dns_name=self.dns_name)
                )
                self.assertEqual(
                    partner.courses_api_url,
                    "https://dummy-{dns_name}.example.com/api/courses/v1/".format(dns_name=self.dns_name)
                )
                self.assertEqual(
                    partner.ecommerce_api_url,
                    "https://ecommerce-dummy-{dns_name}.example.com/".format(dns_name=self.dns_name)
                )
                self.assertEqual(
                    partner.organizations_api_url,
                    "https://dummy-{dns_name}.example.com/api/organizations/v0/"
                )

    def _assert_sites_are_valid(self):
        sites = Site.objects.all()
        partners = Partner.objects.all()

        # There is an extra default site.
        self.assertEqual(len(sites), len(SITES) + 1)
        self.assertEqual(len(partners), len(SITES))

        for site in sites:
            if site.name in SITES:
                site_name = site.name
                self.assertEqual(
                    site.domain,
                    "ecommerce-{site}-{dns_name}.example.com".format(site=site_name, dns_name=self.dns_name)
                )

                site_theme = SiteTheme.objects.get(site=site)
                self.assertEqual(
                    site_theme.theme_dir_name,
                    "dummy.dir"
                )

                site_config = SiteConfiguration.objects.get(site=site)
                self.assertEqual(
                    site_config.partner.short_code,
                    "dummy"
                )

                self.assertEqual(
                    site_config.lms_url_root,
                    ""
                )

                self.assertTrue(site_config.enable_enrollment_codes)
                self.assertEqual(
                    site_config.payment_support_email,
                    "dummy@example.com"
                )

                self.assertEqual(
                    site_config.payment_support_url,
                    "https://dummy-{dns_name}.example.com/contact".format(dns_name=self.dns_name),
                )

                self.assertEqual(
                    site_config.discovery_api_url,
                    "https://discovery-dummy-{dns_name}.example.com/api/v1/".format(dns_name=self.dns_name)
                )

                self.assertEqual(
                    site_config.client_side_payment_processor,
                    "dummy-method"
                )

                self.assertDictEqual(
                    site_config.oauth_settings,
                    "{}"
                )

    def test_missing_required_arguments(self):
        """
        Verify CommandError is raised when required arguments are missing.
        """

        # If a required argument is not specified the system should raise a CommandError
        with self.assertRaises(CommandError):
            call_command(
                "create_sites_and_partners",
                "--dns-name", self.dns_name,
            )

        with self.assertRaises(CommandError):
            call_command(
                "create_sites_and_partners",
                "--theme-path", self.theme_path,
            )

    def test_create_site_and_partner(self):
        """
        Verify that command creates sites and Partners
        """
        call_command(
            "create_sites_and_partners",
            "--dns-name", self.dns_name,
            "--theme-path", self.theme_path
        )
        self._assert_sites_are_valid()

        call_command(
            "create_sites_and_partners",
            "--dns-name", self.dns_name,
            "--theme-path", self.theme_path
        )
        # if we run command with same dns then it will not duplicates the sites and partners.
        self._assert_site_and_partner_are_valid()
