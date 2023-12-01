# Bunny.net DNS Certbot Plugin

### ⚠️ NOTE: THIS IS NO LONGER MAINTAINED. PLEASE [CHECK THIS OUT](https://github.com/mwt/certbot-dns-bunny) INSTEAD. ⚠️

### Information

This plugin is in BETA and works in conjunction with Certbot in order to issue wildcard (or regular) certificates. 

### Prerequisites

You'll need Certbot installed and a configuration file for the plugin. In this case, we'll use `bunny.ini`.

Inside of `bunny.ini`, you should have the following:

    certbot_dns_bunny:dns_bunny_AccessKey = your_access_key_goes_here

Your `AccessKey` can be found here: https://panel.bunny.net/account (under the "API" section).

Once you've created the file, make sure to set safe permissions:

    chmod 600 bunny.ini

### Installation

To begin, clone the repository. 

    git clone https://github.com/doghouch/certbot-dns-bunny.git

Then, perform:

    pip3 install -e /path/to/plugin/repository

Make sure that the installation has completed successfully:

    root@localhost~# certbot plugins
    Saving debug log to /var/log/letsencrypt/letsencrypt.log

    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    * certbot-dns-bunny:dns-bunny
    Description: Obtain certificates using a DNS TXT record.
    Interfaces: IAuthenticator, IPlugin
    Entry point: dns-bunny = certbot_dns_bunny.dns_bunny:Authenticator

    (...)
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

Finally, you can generate a certificate with other plugins, or in "standalone" (certonly) mode:

    certbot certonly --authenticator certbot-dns-bunny:dns-bunny --certbot-dns-bunny:dns-bunny-credentials bunny.ini

Note - valid parameters for the plugin are:

- `--authenticator certbot-dns-bunny:dns-bunny` (this is required)
- `--certbot-dns-bunny:dns-bunny-credentials /path/to/your/bunny.ini` (this is required)
- `--certbot-dns-bunny:dns-bunny-propagation-seconds 120` (optional parameter; default is 120 seconds, however, you can change this to any reasonable number)
