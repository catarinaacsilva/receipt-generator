# Receipt Generator



## Requirements


## Receipt structure

```
{
    "Receipt  Version"    :   "CASSIOPEIA-202102"
    "Receipt Timestamp"    :   "unix timestamp milliseconds"
    "Receipt ID"    :   "UUID v4"
    "Language"    :   "'English'"
    "Self-service point"    :   "http://cassiopeia.id/receipts"
    "Self-service token"    :   "HMAC ( Receipt ID + "cassio0key0peia" )"
    "Privacy Polic"    :   "fingerprint	using SHA256"
    "Consent Status"    :   "consent given" | "consent rejected"
    "Legal Jurisdiction"    :   "'Europe'"
    "Controller"    :   "Identity	legal entity as in the privacy policy"
    "Legal Justification"    :   "'consent'"
    "Method of Collection"    :   "'online web action'"
}
```

1. receipt fingerprint:	digest of the whole receipt up to here (SHA256)
2. digest of method of collection: fingerprint (SHA256) of JavaScript + HTML of the page where the user clicks "I agree"
3. Signed receipt from Controller: RSA2048; key generation and distribution are out of scope


## Cassandra - Database

- Run `./manage.py sync_cassandra` in order to sync your models with Cassandra.
- PK: email and receipt_id (we need two primary keys)
- Important commands:

    - `cqlsh -u cassandra -p cassandra 10.0.12.42`
    - `describe table dht.receipt ;`

## Authors

* **Catarina Silva** - [catarinaacsilva](https://github.com/catarinaacsilva)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details