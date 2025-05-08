# HAProxy & pgbouncer vs pgpoolII

PgPoolII is a generalist software which try to provide features of both a proxy and a connection pooler. Because of this it doesn't do anything too well.

PgBouncer is a simple lightweight specialist which provide only connection pooling, but it does that very well.

HAProxy is specialized proxy, and it performs proxy tasks better than PgPoolII on the same hardware.
Given that PgBouncer is so lightweight, it should be colocated on the same servers as the control panes and worker nodes. Thus on the same hardwares, HAProxy + PgBouncer would most likely outperforms PgPoolII in most cases.

PgPoolII therefore is best use in case which strict control over connection requests has been obtained. So that PgPoolII would receive only optimal amount of requests for its server hardwares e.g. test environments. Since it is simpler to setup and configure relative to HAProxy + PgBouncer.
