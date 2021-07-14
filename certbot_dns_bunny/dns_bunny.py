import json

import requests
import logging

import zope.interface

from certbot import errors
from certbot import interfaces
from certbot.plugins import dns_common

@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)

class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for Bunny.net

    """

    description = "Obtain certificates using a DNS TXT record."

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add):
        super(Authenticator, cls).add_parser_arguments(
            add, default_propagation_seconds=120
        )
        add("credentials", help="Bunny.net Credentials INI file.")

    def more_info(self):
        return (
            "This plugin configures a DNS TXT record to respond to a dns-01 challenge using "
            + "the Bunny.net API."
        )

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            "credentials",
            "Bunny.net credentials INI file",
            {
                "AccessKey": "API Key for Bunny.net account.",
            },
        )

    def _perform(self, domain, validation_name, validation):
        """
            Generate and save challenges.
        """
        found = None
        real_validation_name = _clean_up_subdomain(validation_name)
        real_domain = _grab_domain_only(domain)
        headers = {"Content-Type": "application/json", "Accept": "application/json", "AccessKey": self.credentials.conf("AccessKey")}
        zone_list = requests.get("https://api.bunny.net/dnszone/", headers=headers)
        try:
            json_data = json.loads(zone_list.text)
            if "Message" in json_data:
                # Throw PluginError; 99.95% of the time the existence of the"Message" parameter indicates an invalid AccessKey.
                raise errors.PluginError("Failed to contact Bunny.net API; authentication failed.")
            for item in json_data:
                if item["Domain"] == real_domain:
                    found = True
                    # add new challenge TXT record
                    _add_txt_record(headers=headers, domain_id=item["Id"], name=real_validation_name, value=validation, ttl=60)
                    break
            if not found:
                raise errors.PluginError("The domain \"" + real_domain + "\" could not be found under your account.")
        except Exception as e:
            raise errors.PluginError(e)

    def _cleanup(self, domain, validation_name, validation):
        """
            Clean up challenge records.
        """
        real_validation_name = _clean_up_subdomain(validation_name)
        real_domain = _grab_domain_only(domain)
        headers = {"Content-Type": "application/json", "Accept": "application/json", "AccessKey": self.credentials.conf("AccessKey")}
        zone_list = requests.get("https://api.bunny.net/dnszone/", headers=headers)
        try:
            json_data = json.loads(zone_list.text)
            if "Message" in json_data:
                # Throw PluginError; 99.95% of the time the existence of the"Message" parameter indicates an invalid AccessKey.
                raise errors.PluginError("Failed to contact Bunny.net API; authentication failed.")
            for item in json_data:
                if item["Domain"] == real_domain:
                    for record in item["Records"]:
                        if record["Name"] == real_validation_name and record["Type"] == 3 and record["Value"] == validation:
                            # Record matches the validation name, is a TXT record and has the correct challenge value.
                            _delete_txt_record(headers=headers, domain_id=item["Id"], id=record["Id"])
                            break
                    break
        except:
            raise errors.PluginError("Could not contact Bunny.net API for cleanup.")


# ----- HELPERS ----- #

def _delete_txt_record(headers: dict, domain_id: int, id: int):
    """
        Deletes TXT record based on ID.
    """
    resp = requests.delete("https://api.bunny.net/dnszone/" + str(domain_id) + "/records/" + str(id), headers=headers)

    if resp.status_code != 204:
        raise errors.PluginError("API Call Failed: " + resp.text)

def _add_txt_record(headers: dict, domain_id: int, name: str, value: str, ttl: int):
    """
        Adds TXT record on BunnyDNS.

        Note: Type 3 == TXT record.
    """
    data = json.dumps({"Name": name, "Value": value, "Ttl": ttl, "Type": 3,"PullZoneId": 0})

    resp = requests.put("https://api.bunny.net/dnszone/" + str(domain_id) + "/records", headers=headers, data=data)

    if resp.status_code != 204:
        raise errors.PluginError("API Call Failed: " + resp.text)

def _clean_up_subdomain(validation_name: str):
    """
        Cleans up domains for BunnyDNS.

        Examples:
            _acme-challenge.www.example.com                     => _acme-challenge.www
            _acme-challenge.some.long.subdomain.example.com     => _acme-challenge.some.long.subdomain
    """
    try:
        extract = validation_name.split(".")[:-2]
        real_validation_name = ""
        for counter, segment in enumerate(extract):
            real_validation_name += segment
            if counter + 1 != len(extract):
                real_validation_name += "."
        return real_validation_name
    except:
        raise errors.PluginError("Plugin encountered an unexpected error.") 

def _grab_domain_only(domain: str):
    """
        Grabs the domain.

        Examples:
            _acme-challenge.www.example.com                     => example.com
            _acme-challenge.some.long.subdomain.example.com     => example.com
    """
    try:
        extract = domain.split(".")[-2::]
        real_domain = ""
        for counter, segment in enumerate(extract):
            real_domain += segment
            if counter + 1 != len(extract):
                real_domain += "."
        return real_domain
    except:
        raise errors.PluginError("Plugin encountered an unexpected error.") 
