
# put the query here or copy it into kibana console
curl -XPOST 'localhost:9200/travel/_search?size=0&pretty' -H 'Content-Type: application/json' -d'
	@@ PUT QUERY HERE @@
'


# histograma tiempos de viaje
{
    "aggs" : {
        "tiempos_de_viaje" : {
            "histogram" : {
                "field" : "tviaje",
                "interval" : 15
            },
            "aggs" : {
                "cantidad" : {
                    "sum" : {
                        "field" : "factor_expansion"
                    }
                },
                "acumulado" : {
                    "cumulative_sum" : {
                        "buckets_path" : "cantidad"
                    }
                }
            }
        }
    },
    "size" : 0
}


