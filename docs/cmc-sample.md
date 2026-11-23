# Real CoinMarketCap API calls (sample)

Captured from GitHub Actions with the project's key (the key is sent as the `X-CMC_PRO_API_KEY` header and is never stored in this repository).

## `GET /v1/cryptocurrency/listings/latest?start=1&limit=2&convert=USD&sort=market_cap`

HTTP 200

```json
{
  "data": [
    {
      "id": 1,
      "name": "Bitcoin",
      "symbol": "BTC",
      "slug": "bitcoin",
      "infinite_supply": false,
      "circulating_supply": 20116112,
      "total_supply": 20116112,
      "max_supply": 21000000,
      "date_added": "2010-07-13T00:00:00.000Z",
      "num_market_pairs": 12787,
      "cmc_rank": 1,
      "last_updated": "2026-11-23T07:57:33.031Z",
      "tvl_ratio": null,
      "platform": null,
      "self_reported_circulating_supply": null,
      "self_reported_market_cap": null,
      "minted_market_cap": 1235241397323.62,
      "quote": {
        "USD": {
          "price": 61405.57366769571,
          "volume_24h": 27835029073.44832,
          "cex_volume_24h": 27754599913.09688,
          "dex_volume_24h": 80429160.35143782,
          "volume_change_24h": -23.173973410937,
          "percent_change_1h": -0.151916283888,
          "percent_change_24h": 3.98796842785,
          "percent_change_7d": -5.473739474558,
          "percent_change_30d": -23.859735378166,
          "percent_change_60d": -27.326031635455,
          "percent_change_90d": -22.961948633463,
          "market_cap": 1235241397323.6177,
          "market_cap_dominance": 58.9216,
          "fully_diluted_market_cap": 1289517047021.61,
          "tvl": null,
          "last_updated": "2026-11-23T07:57:33.031Z"
        }
      },
      "tags": [
        "mineable",
        "pow",
        "sha-256",
        "store-of-value",
        "state-channel",
        "coinbase-ventures-portfolio",
        "three-arrows-capital-portfolio",
        "polychain-capital-portfolio",
        "binance-labs-portfolio",
        "blockchain-capital-portfolio",
        "boostvc-portfolio",
        "cms-holdings-portfolio",
        "dcg-portfolio",
        "dragonfly-capital-portfolio",
        "electric-capital-portfolio",
        "fabric-ventures-portfolio",
        "framework-ventures-portfolio",
        "galaxy-digital-portfolio",
        "huobi-capital-portfolio",
        "alameda-research-portfolio",
        "a16z-portfolio",
        "1confirmation-portfolio",
        "winklevoss-capital-portfolio",
        "usv-portfolio",
        "placeholder-ventures-portfolio",
        "pantera-capital-portfolio",
        "multicoin-capital-portfolio",
        "paradigm-portfolio",
        "bitcoin-ecosystem",
        "layer-1",
        "ftx-bankruptcy-estate",
        "2017-2018-alt-season",
        "us-strategic-crypto-reserve",
        "binance-ecosystem",
        "binance-listing",
        "sec-cftc-token-taxonomy",
        "sec-cftc-digital-commodities"
      ]
    },
    {
      "id": 1027,
      "name": "Ethereum",
      "symbol": "ETH",
      "slug": "ethereum",
      "infinite_supply": true,
      "circulating_supply": 122244884.63845614,
      "total_supply": 122244884.63845614,
      "max_supply": null,
      "date_added": "2015-08-07T00:00:00.000Z",
      "num_market_pairs": 14438,
      "cmc_rank": 2,
      "last_updated": "2026-11-23T07:57:33.182Z",
      "tvl_ratio": null,
      "platform": null,
      "self_reported_circulating_supply": null,
      "self_reported_market_cap": null,
      "minted_market_cap": 210365648948.91,
      "quote": {
        "USD": {
          "price": 1720.8544109725137,
          "volume_24h": 9131418391.560673,
          "cex_volume_24h": 9003764648.509142,
          "dex_volume_24h": 127653743.05152851,
          "volume_change_24h": -19.251657558615,
          "percent_change_1h": -0.203960122782,
          "percent_change_24h": 3.397948077891,
          "percent_change_7d": -5.495002916144,
          "percent_change_30d": -27.481668615916,
          "percent_change_60d": -36.13350599356,
          "percent_change_90d": -30.71249139253,
          "market_cap": 210365648948.9133,
          "market_cap_dominance": 10.0371,
          "fully_diluted_market_cap": 210365648948.91,
          "tvl": null,
          "last_updated": "2026-11-23T07:57:33.182Z"
        }
      },
      "tags": [
        "pos",
        "smart-contracts",
        "ethereum-ecosystem",
        "coinbase-ventures-portfolio",
        "three-arrows-capital-portfolio",
        "polychain-capital-portfolio",
        "binance-labs-portfolio",
        "blockchain-capital-portfolio",
        "boostvc-portfolio",
        "cms-holdings-portfolio",
        "dcg-portfolio",
        "dragonfly-capital-portfolio",
        "electric-capital-portfolio",
        "fabric-ventures-portfolio",
        "framework-ventures-portfolio",
        "hashkey-capital-portfolio",
        "kenetic-capital-portfolio",
        "huobi-capital-portfolio",
        "alameda-research-portfolio",
        "a16z-portfolio",
        "1confirmation-portfolio",
        "winklevoss-capital-portfolio",
        "usv-portfolio",
        "placeholder-ventures-portfolio",
        "pantera-capital-portfolio",
        "multicoin-capital-portfolio",
        "paradigm-portfolio",
        "ethereum-pow-ecosystem",
        "layer-1",
        "ftx-bankruptcy-estate",
        "sora-ecosystem",
        "rsk-rbtc-ecosystem",
        "world-liberty-financial-portfolio",
        "us-strategic-crypto-reserve",
        "binance-ecosystem",
        "binance-listing",
        "abstract-chain-ecosystem",
        "unichain-ecosystem",
        "soneium-ecosystem",
        "sophon-ecosystem",
        "sec-cftc-token-taxonomy",
        "sec-cftc-digital-commodities",
        "anubis-ecosystem",
        "robinhood-ecosystem"
      ]
    }
  ],
  "status": {
    "timestamp": "2026-11-23T07:57:39.746Z",
    "error_code": 0,
    "error_message": null,
    "elapsed": 15,
    "credit_count": 1,
    "total_count": 7890,
    "notice": null
  }
}
```

## `GET /v1/global-metrics/quotes/latest?convert=USD`

HTTP 200

```json
{
  "data": {
    "quote": {
      "USD": {
        "total_market_cap": 2096413938286.098,
        "total_volume_24h": 60345828760.36,
        "total_volume_24h_reported": 435433397518.7,
        "altcoin_volume_24h": 32438776691.915897,
        "altcoin_volume_24h_reported": 250614212923.10187,
        "altcoin_market_cap": 860912945724.0496,
        "defi_volume_24h": 8013991106.93348,
        "defi_market_cap": 60752744222.655945,
        "defi_volume_24h_reported": 101795939239.71962,
        "defi_24h_percentage_change": 1.8368526654,
        "stablecoin_volume_24h": 61474409186.67642,
        "stablecoin_volume_24h_reported": 422437172277.0823,
        "stablecoin_market_cap": 267503566830.54398,
        "stablecoin_24h_percentage_change": -16.7624313025,
        "derivatives_volume_24h": 594593042752.2449,
        "derivatives_volume_24h_reported": 622040960132.5199,
        "derivatives_24h_percentage_change": 11.0547969761,
        "total_market_cap_yesterday": 2030931216246.0828,
        "total_volume_24h_yesterday": 72122696784.28,
        "total_market_cap_yesterday_percentage_change": 3.22427079,
        "total_volume_24h_yesterday_percentage_change": -16.32893465,
        "last_updated": "2026-11-23T07:55:59.999Z"
      }
    },
    "btc_dominance": 58.934019183832,
    "eth_dominance": 10.036365801228,
    "active_cryptocurrencies": 7900,
    "total_cryptocurrencies": 40266,
    "active_market_pairs": 106246,
    "active_exchanges": 989,
    "total_exchanges": 13449,
    "last_updated": "2026-11-23T07:55:59.999Z",
    "eth_dominance_yesterday": 10.01687298,
    "btc_dominance_yesterday": 58.48178773,
    "eth_dominance_24h_percentage_change": 0.019492821228,
    "btc_dominance_24h_percentage_change": 0.452231453832,
    "defi_volume_24h": 8013991106.93348,
    "defi_volume_24h_reported": 101795939239.71962,
    "defi_market_cap": 60752744222.655945,
    "defi_24h_percentage_change": 1.83685266543,
    "stablecoin_volume_24h": 61474409186.67642,
    "stablecoin_volume_24h_reported": 422437172277.0823,
    "stablecoin_market_cap": 267503566830.54398,
    "stablecoin_24h_percentage_change": -16.762431302484,
    "derivatives_volume_24h": 594593042752.2449,
    "derivatives_volume_24h_reported": 622040960132.5199,
    "derivatives_24h_percentage_change": 11.054796976083,
    "total_crypto_dex_currencies": 66750455,
    "today_incremental_crypto_number": 0,
    "past_24h_incremental_crypto_number": 59577,
    "past_7d_incremental_crypto_number": 397618,
    "past_30d_incremental_crypto_number": 2019556,
    "today_change_percent": 4.6441653e-05,
    "tracked_yearly_number": {
      "maxIncrementalNumber": 7681147,
      "minIncrementalNumber": 31,
      "maxIncrementalDate": "2026-03-19T00:00:00.000Z",
      "minIncrementalDate": "2026-11-23T00:00:00.000Z"
    }
  },
  "status": {
    "timestamp": "2026-11-23T07:57:39.918Z",
    "error_code": 0,
    "error_message": null,
    "elapsed": 10,
    "credit_count": 1,
    "notice": null
  }
}
```

## `GET /v3/fear-and-greed/historical?limit=2`

HTTP 200

```json
{
  "data": [
    {
      "timestamp": "1795305600",
      "value": 8,
      "value_classification": "Extreme fear"
    },
    {
      "timestamp": "1795219200",
      "value": 8,
      "value_classification": "Extreme fear"
    }
  ],
  "status": {
    "timestamp": "2026-11-23T07:57:40.081Z",
    "error_code": "0",
    "error_message": "",
    "elapsed": 4,
    "credit_count": 1
  }
}
```

## `GET /v1/key/info`

HTTP 200

```json
{
  "status": {
    "timestamp": "2026-11-23T07:57:40.244Z",
    "error_code": 0,
    "error_message": null,
    "elapsed": 6,
    "credit_count": 0,
    "notice": null
  },
  "data": {
    "plan": {
      "credit_limit_monthly": 15000,
      "credit_limit_monthly_reset": "In 7 days, 16 hours, 2 minutes",
      "credit_limit_monthly_reset_timestamp": "2026-12-01T00:00:00.000Z",
      "rate_limit_minute": 50
    },
    "usage": {
      "current_month": {
        "credits_used": 7,
        "credits_left": 14993
      }
    }
  }
}
```
