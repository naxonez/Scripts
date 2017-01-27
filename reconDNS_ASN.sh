##################################################################
# Script para obtener IP - DNS - ASN de un listado de dominios   #
##################################################################
#                       Created by @NaxoneZ                      #
##################################################################
#!/bin/bash

echo "dominio - IP - DNS - ASN" >> domains_Final.txt

for domain in `cat dns.txt`
do
        ip=$(host -t a $domain | grep "address" | cut -d' ' -f4)
        if [[ $domain == *".mobi" ]]; then
                dns=$(whois -h whois.dotmobiregistry.net domain $domain |  grep "Name Server:" | cut -d':' -f2 | xargs)
        else
                dns=$(whois -h whois.verisign-grs.com domain $domain |  grep "Name Server:" | cut -d':' -f2 | xargs)

        fi
        if [[ -z $ip ]]; then
                ip=$(host -t a www.$domain | grep "address" | cut -d' ' -f4)
                asn=$(whois $ip | grep "origin:" | cut -d':' -f2 | xargs)
        else
                asn=$(whois $ip | grep "origin:" | cut -d':' -f2 | xargs)

        fi
        echo "$domain | $ip | $dns | $asn"
        echo "$domain | $ip | $line | $dns | $asn" >> domains_Final.txt

   sleep 1
done
