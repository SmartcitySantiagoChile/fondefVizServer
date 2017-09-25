# README

## Indicadores Varios


### 

```json
POST /travel/_search
{
  "size": 0, 
  "query": {
    "bool": {
      "filter": 
      [
        {
          "range": {
            "tiempo_subida": {
              "time_zone": "America/Santiago",
              "gte": "13/03/2016 00:00",
              "lte": "15/03/2016 23:59",
              "format": "dd/MM/yyyy HH:mm"
            }
          }
        },
        {
          "terms": {
            "tipodia": ["0"]
          }
        }
      ]
    }
  },
  "aggs": {
    "documentos" : { "value_count" : { "field" : "id" }},
    "viajes" : { "sum" : { "field" : "factor_expansion" }},
    "tviaje" : { "stats" : { "field" : "tviaje" }},
    "n_etapas" : { "stats" : { "field" : "n_etapas" }},
    "distancia_ruta" : { "stats" : { "field" : "distancia_ruta" }},
    "distancia_eucl" : { "stats" : { "field" : "distancia_eucl" }}
  }
}
```

## Mapa de viajes de 4 etapas

```json
POST /travel/_search
{
  "size": 0, 
  "query": {
    "bool": {
      "filter": 
      [
        {
          "range": {
            "tiempo_subida": {
              "time_zone": "America/Santiago",
              "gte": "13/03/2016 00:00",
              "lte": "15/03/2016 23:59",
              "format": "dd/MM/yyyy HH:mm"
            }
          }
        },
        {
          "range": { "n_etapas": { "gte": "4" }}
        },
        {
          "terms": {
            "tipodia": ["0"]
          }
        }
      ]
    }
  },
  "aggs": {
    "by_zone": {
      "terms": {
        "field": "zona_subida",
        "size": 1000
      },
      "aggs": {
        "tviaje"   : { "avg" : { "field" : "tviaje" }},
        "distancia_ruta" : { "avg" : { "field" : "distancia_ruta" }},
        "distancia_eucl" : { "avg" : { "field" : "distancia_eucl" }},
        "n_etapas" : { "stats" : { "field" : "n_etapas" }}
      }
    }
  }
}
```



## Mapa, zonas y sectores

### Zonas y sectores

Se obtuvieron los siguientes sectores a partir del archivo `Diccionario-Zonificaciones.csv` de zonificaciones 777 y de las comunas de interés presentes en el GeoJSON `/static/travel/data/zonificacion777.geojson`.

```
Lo Barnechea 
324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 


Las Condes
287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 


Providencia
494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 


Santiago
1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 
```



### Query

Se diseñó la versión 1, pero ya que `elasticsearch-dsl-py` no soporta la agregación `filters` (al parecer no andaba bien y la removieron), se prefirió la segunda versión, más verbosa.

Ambas consultas son equivalentes en términos de resultados. La versión 1 es menos verbosa, pero la respuesta de v2 pesa menos.

v1: ~ ms, 1.71MB (raw), ??
v2: ~ ms, 1.15MB (raw), 560KB (network)

Versión raw medida con: https://mothereff.in/byte-counter


#### Versión 1 (deseable? / menos verbosa)

```json
POST /travel/_search
{
  "size": 0, 
  "query": {
    "bool": {
      "filter": 
      [
        {
          "range": {
            "tiempo_subida": {
              "time_zone": "America/Santiago",
              "gte": "13/03/2016 00:00",
              "lte": "15/03/2016 23:59",
              "format": "dd/MM/yyyy HH:mm"
            }
          }
        },
        {
          "terms": {
            "tipodia": ["0"]
          }
        }
      ]
    }
  },
  "aggs": {
    "by_sectors": {
      "filters": {
        "other_bucket_key": "no_sector", 
        "filters": {
            "LAS CONDES": { "terms": { "zona_bajada": ["287", "288", "289", "290", "291", "292", "293", "294", "295", "296", "297", "298", "299", "300", "301", "302", "303", "304", "305", "306", "307", "308", "309", "310", "311", "312", "313", "314", "315", "316", "317", "318", "319", "320", "321", "322", "323"]}},
            "LO BARNECHEA": { "terms": { "zona_bajada": ["324", "325", "326", "327", "328", "329", "330", "331", "332", "333", "334", "335", "336"]}},
            "PROVIDENCIA": { "terms": { "zona_bajada": ["494", "495", "496", "497", "498", "499", "500", "501", "502", "503", "504", "505", "506", "507", "508", "509", "510", "511", "512", "513", "514", "515", "516"]}},
            "SANTIAGO": { "terms": { "zona_bajada": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52"]}}
        }
      },
      "aggs": {
        "by_sector_and_zone": {
          "terms": {
            "field": "zona_subida",
            "size": 1000
          },
          "aggs": {
            "tviaje"   : { "avg" : { "field" : "tviaje" }},
            "n_etapas" : { "avg" : { "field" : "n_etapas" }},
            "distancia_ruta" : { "avg" : { "field" : "distancia_ruta" }},
            "distancia_eucl" : { "avg" : { "field" : "distancia_eucl" }}
          }
        }
      }
    }
  }
}
```

### Versión 2 (implementada / workaround)

```json
POST /travel/_search
{
  "size": 0, 
  "query": {
    "bool": {
      "filter": 
      [
        {
          "range": {
            "tiempo_subida": {
              "time_zone": "America/Santiago",
              "gte": "13/03/2016 00:00",
              "lte": "15/03/2016 23:59",
              "format": "dd/MM/yyyy HH:mm"
            }
          }
        },
        {
          "terms": {
            "tipodia": ["0"]
          }
        }
      ]
    }
  },
  "aggs": {
    "LAS CONDES": {
      "filter": {
        "terms": { 
          "zona_bajada": ["287", "288", "289", "290", "291", "292", "293", "294", "295", "296", "297", "298", "299", "300", "301", "302", "303", "304", "305", "306", "307", "308", "309", "310", "311", "312", "313", "314", "315", "316", "317", "318", "319", "320", "321", "322", "323"]}},
      "aggs": {
        "by_zone": {
          "terms": {
            "field": "zona_subida",
            "size": 1000
          },
          "aggs": {
            "tviaje"   : { "avg" : { "field" : "tviaje" }},
            "n_etapas" : { "avg" : { "field" : "n_etapas" }},
            "distancia_ruta" : { "avg" : { "field" : "distancia_ruta" }},
            "distancia_eucl" : { "avg" : { "field" : "distancia_eucl" }}
          }
        }
      }
    },
    "LO BARNECHEA": {
        "filter": { "terms": { "zona_bajada": ["324", "325", "326", "327", "328", "329", "330", "331", "332", "333", "334", "335", "336"]}},
      "aggs": {
        "by_zone": {
          "terms": {
            "field": "zona_subida",
            "size": 1000
          },
          "aggs": {
            "tviaje"   : { "avg" : { "field" : "tviaje" }},
            "n_etapas" : { "avg" : { "field" : "n_etapas" }},
            "distancia_ruta" : { "avg" : { "field" : "distancia_ruta" }},
            "distancia_eucl" : { "avg" : { "field" : "distancia_eucl" }}
          }
        }
      }
    },
    "PROVIDENCIA": {
      "filter": { "terms": { "zona_bajada": ["494", "495", "496", "497", "498", "499", "500", "501", "502", "503", "504", "505", "506", "507", "508", "509", "510", "511", "512", "513", "514", "515", "516"]}},
      "aggs": {
        "by_zone": {
          "terms": {
            "field": "zona_subida",
            "size": 1000
          },
          "aggs": {
            "tviaje"   : { "avg" : { "field" : "tviaje" }},
            "n_etapas" : { "avg" : { "field" : "n_etapas" }},
            "distancia_ruta" : { "avg" : { "field" : "distancia_ruta" }},
            "distancia_eucl" : { "avg" : { "field" : "distancia_eucl" }}
          }
        }
      }
    },
    "SANTIAGO": {
      "filter": { "terms": { "zona_bajada": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52"]}},
      "aggs": {
        "by_zone": {
          "terms": {
            "field": "zona_subida",
            "size": 1000
          },
          "aggs": {
            "tviaje"   : { "avg" : { "field" : "tviaje" }},
            "n_etapas" : { "avg" : { "field" : "n_etapas" }},
            "distancia_ruta" : { "avg" : { "field" : "distancia_ruta" }},
            "distancia_eucl" : { "avg" : { "field" : "distancia_eucl" }}
          }
        }
      }
    }
  }
}
```