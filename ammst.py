from collections import namedtuple
import altair as alt
import math
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objs as go

import datetime
import driftpy
import mango
import requests

# from driftpy.constants.markets import MARKETS
assets = ['SOL', 'BTC', 'ETH', 'LUNA', 'AVAX', 'BNB', 'MATIC', 'ATOM', 'DOT', 'ADA', 'ALGO', 'FTT', 'LTC']
MARKET_INDEX_TO_PERP = {i: ast+'-PERP' for i,ast in enumerate(assets)}
MARKET_PERP_TO_INDEX = {v: k for k,v in MARKET_INDEX_TO_PERP.items()}

# MARKET_INDEX_TO_PERP = {i: MARKETS[i].symbol for i in range(len(MARKETS))}
# MARKET_PERP_TO_INDEX = {MARKETS[i].symbol: i for i in range(len(MARKETS))}

FUNDING_SCALE = 1

@st.cache(ttl=600)
def make_funding_table(drift):
    # drift_markets = {v: str(k) for k,v in driftsummary.MARKET_INDEX_TO_PERP.items()}
    ASSETS=[]
    for x in range(len(list(MARKET_INDEX_TO_PERP.values()))):
        ASSETS.append(MARKET_INDEX_TO_PERP[x].split('-')[0])
        #("SOL", "BTC", "ETH", "LUNA", "AVAX", "BNB", "MATIC")
    print(ASSETS)
    assert(ASSETS[0]=='SOL')

    EXTRAS = ['SRM']
    for extra in EXTRAS:
        ASSETS.append(extra)
    
    # # import requests
    # def load_mango_data(market="SOL-PERP"):
    #     # Find the addresses associated with the Perp market
    #     perp_stub = context.market_lookup.find_by_symbol("perp:" + market)
    #     # Load the rest of the on-chain metadata of the market
    #     perp_market = mango.ensure_market_loaded(context, perp_stub)
    #     # z = perp_market.fetch_funding(context)
    #     return perp_market
    

    mango_markets = {
        "BTC": "DtEcjPLyD4YtTBB4q8xwFZ9q49W89xZCZtJyrGebi5t8",
        "SOL": "2TgaaVoHgnSeEtXvWTx13zQeTf4hYWAMEiMQdcG6EwHi",
        "ETH": "DVXWg6mfwFvHQbGyaHke4h3LE9pSkgbooDSDgA4JBC8d",
        "LUNA": "BCJrpvsB2BJtqiDgKVC4N6gyX1y24Jz96C6wMraYmXss",
        "AVAX": "EAC7jtzsoQwCbXj1M3DapWrNLnc3MBwXAarvWDPr2ZV9",
        "BNB": "CqxX2QupYiYafBSbA519j4vRVxxecidbh2zwX66Lmqem",
        'SRM': "4GkJj2znAr2pE2PBbak66E12zjCs2jkmeafiJwDVM9Au",
        'RAY': "DtEcjPLyD4YtTBB4q8xwFZ9q49W89xZCZtJyrGebi5t8",
        'MNGO': "DtEcjPLyD4YtTBB4q8xwFZ9q49W89xZCZtJyrGebi5t8",
        'ADA': "Bh9UENAncoTEwE7NDim8CdeM1GPvw6xAT4Sih2rKVmWB",
        'FTT': "AhgEayEGNw46ALHuC5ASsKyfsJzAm5JY8DWqpGMQhcGC",
    }
    mango_fund_rate = [np.nan]*len(ASSETS)
    mango_oi = [np.nan]*len(ASSETS)
    # try:
    for i,x in enumerate((ASSETS)):
        if x in mango_markets.keys():
            mfund = load_mango_data(x+"-PERP")
            if mfund is not None:
                mm = mfund.fetch_funding(context)
                mango_fund_rate[i] = mm.rate
                mango_oi[i] = mm.open_interest
    # except:
    #     pass


    try:
        dydx_url = 'https://api.dydx.exchange/v3/markets'
        global dydx_data
        dydx_data = requests.get(dydx_url).json()
    except:
        dydx_data = {"markets":{"BTC-USD":{"market":"BTC-USD","status":"ONLINE","baseAsset":"BTC","quoteAsset":"USD","stepSize":"0.0001","tickSize":"1","indexPrice":"42968.3170","oraclePrice":"42922.8550","priceChange24H":"-1203.984000","nextFundingRate":"0.0000037402","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.001","type":"PERPETUAL","initialMarginFraction":"0.05","maintenanceMarginFraction":"0.03","volume24H":"1640902107.353700","trades24H":"198273","openInterest":"5439.2241","incrementalInitialMarginFraction":"0.01","incrementalPositionSize":"1.5","maxPositionSize":"170","baselinePositionSize":"9","assetResolution":"10000000000","syntheticAssetId":"0x4254432d3130000000000000000000"},"SUSHI-USD":{"market":"SUSHI-USD","status":"ONLINE","baseAsset":"SUSHI","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.001","indexPrice":"4.3138","oraclePrice":"4.3110","priceChange24H":"-0.428218","nextFundingRate":"-0.0000052310","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"3506719.908000","trades24H":"1828","openInterest":"3046758.4","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"10000","maxPositionSize":"491000","baselinePositionSize":"49200","assetResolution":"10000000","syntheticAssetId":"0x53555348492d370000000000000000"},"AVAX-USD":{"market":"AVAX-USD","status":"ONLINE","baseAsset":"AVAX","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.01","indexPrice":"88.9606","oraclePrice":"88.9100","priceChange24H":"-0.359377","nextFundingRate":"0.0000111770","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"77383612.420000","trades24H":"21226","openInterest":"526110.3","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"1800","maxPositionSize":"91000","baselinePositionSize":"9000","assetResolution":"10000000","syntheticAssetId":"0x415641582d37000000000000000000"},"1INCH-USD":{"market":"1INCH-USD","status":"ONLINE","baseAsset":"1INCH","quoteAsset":"USD","stepSize":"1","tickSize":"0.001","indexPrice":"1.7700","oraclePrice":"1.7675","priceChange24H":"-0.146723","nextFundingRate":"-0.0000463210","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"10","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"3227348.146000","trades24H":"2211","openInterest":"6173663","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"35000","maxPositionSize":"1700000","baselinePositionSize":"170000","assetResolution":"10000000","syntheticAssetId":"0x31494e43482d370000000000000000"},"ETH-USD":{"market":"ETH-USD","status":"ONLINE","baseAsset":"ETH","quoteAsset":"USD","stepSize":"0.001","tickSize":"0.1","indexPrice":"3023.8912","oraclePrice":"3019.3671","priceChange24H":"-206.026197","nextFundingRate":"-0.0000115577","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.01","type":"PERPETUAL","initialMarginFraction":"0.05","maintenanceMarginFraction":"0.03","volume24H":"1357856566.385000","trades24H":"172305","openInterest":"88254.870","incrementalInitialMarginFraction":"0.01","incrementalPositionSize":"28","maxPositionSize":"2820","baselinePositionSize":"140","assetResolution":"1000000000","syntheticAssetId":"0x4554482d3900000000000000000000"},"XMR-USD":{"market":"XMR-USD","status":"ONLINE","baseAsset":"XMR","quoteAsset":"USD","stepSize":"0.01","tickSize":"0.1","indexPrice":"177.1264","oraclePrice":"176.7150","priceChange24H":"-8.281115","nextFundingRate":"-0.0000066527","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"1165485.516000","trades24H":"1225","openInterest":"23382.55","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"200","maxPositionSize":"6000","baselinePositionSize":"400","assetResolution":"100000000","syntheticAssetId":"0x584d522d3800000000000000000000"},"COMP-USD":{"market":"COMP-USD","status":"ONLINE","baseAsset":"COMP","quoteAsset":"USD","stepSize":"0.01","tickSize":"0.1","indexPrice":"131.2077","oraclePrice":"131.2000","priceChange24H":"-13.361681","nextFundingRate":"-0.0000062885","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"4050490.079000","trades24H":"2469","openInterest":"65502.97","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"330","maxPositionSize":"16600","baselinePositionSize":"1700","assetResolution":"100000000","syntheticAssetId":"0x434f4d502d38000000000000000000"},"ALGO-USD":{"market":"ALGO-USD","status":"ONLINE","baseAsset":"ALGO","quoteAsset":"USD","stepSize":"1","tickSize":"0.001","indexPrice":"0.9551","oraclePrice":"0.9540","priceChange24H":"-0.076083","nextFundingRate":"-0.0000072367","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"10","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"3987185.189000","trades24H":"3157","openInterest":"7702958","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"55000","maxPositionSize":"2700000","baselinePositionSize":"275000","assetResolution":"1000000","syntheticAssetId":"0x414c474f2d36000000000000000000"},"BCH-USD":{"market":"BCH-USD","status":"ONLINE","baseAsset":"BCH","quoteAsset":"USD","stepSize":"0.01","tickSize":"0.1","indexPrice":"333.8701","oraclePrice":"332.5600","priceChange24H":"-10.949868","nextFundingRate":"-0.0000058063","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"12794211.979000","trades24H":"3159","openInterest":"39548.67","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"170","maxPositionSize":"8300","baselinePositionSize":"840","assetResolution":"100000000","syntheticAssetId":"0x4243482d3800000000000000000000"},"CRV-USD":{"market":"CRV-USD","status":"ONLINE","baseAsset":"CRV","quoteAsset":"USD","stepSize":"1","tickSize":"0.001","indexPrice":"3.1460","oraclePrice":"3.1500","priceChange24H":"-0.325781","nextFundingRate":"-0.0000258473","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"10","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"11792139.878000","trades24H":"4266","openInterest":"9059504","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"37000","maxPositionSize":"1900000","baselinePositionSize":"190000","assetResolution":"1000000","syntheticAssetId":"0x4352562d3600000000000000000000"},"UNI-USD":{"market":"UNI-USD","status":"ONLINE","baseAsset":"UNI","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.001","indexPrice":"11.2410","oraclePrice":"11.2600","priceChange24H":"-1.009000","nextFundingRate":"0.0000022992","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"5207393.784800","trades24H":"2928","openInterest":"1311918.6","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"4000","maxPositionSize":"210000","baselinePositionSize":"20800","assetResolution":"10000000","syntheticAssetId":"0x554e492d3700000000000000000000"},"MKR-USD":{"market":"MKR-USD","status":"ONLINE","baseAsset":"MKR","quoteAsset":"USD","stepSize":"0.001","tickSize":"1","indexPrice":"2073.8600","oraclePrice":"2074.2074","priceChange24H":"-166.270000","nextFundingRate":"0.0000125000","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.01","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"4563864.002000","trades24H":"704","openInterest":"8164.437","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"40","maxPositionSize":"2000","baselinePositionSize":"200","assetResolution":"1000000000","syntheticAssetId":"0x4d4b522d3900000000000000000000"},"LTC-USD":{"market":"LTC-USD","status":"ONLINE","baseAsset":"LTC","quoteAsset":"USD","stepSize":"0.01","tickSize":"0.1","indexPrice":"131.7110","oraclePrice":"131.6400","priceChange24H":"-7.459234","nextFundingRate":"-0.0000227146","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"11217188.737000","trades24H":"3652","openInterest":"180424.74","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"560","maxPositionSize":"28000","baselinePositionSize":"2800","assetResolution":"100000000","syntheticAssetId":"0x4c54432d3800000000000000000000"},"EOS-USD":{"market":"EOS-USD","status":"ONLINE","baseAsset":"EOS","quoteAsset":"USD","stepSize":"1","tickSize":"0.001","indexPrice":"2.5220","oraclePrice":"2.5174","priceChange24H":"-0.147346","nextFundingRate":"0.0000057040","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"10","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"3012338.275000","trades24H":"2513","openInterest":"6094188","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"22000","maxPositionSize":"1100000","baselinePositionSize":"110000","assetResolution":"1000000","syntheticAssetId":"0x454f532d3600000000000000000000"},"DOGE-USD":{"market":"DOGE-USD","status":"ONLINE","baseAsset":"DOGE","quoteAsset":"USD","stepSize":"10","tickSize":"0.0001","indexPrice":"0.1496","oraclePrice":"0.1497","priceChange24H":"-0.009766","nextFundingRate":"-0.0000114947","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"100","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"9073625.550000","trades24H":"3914","openInterest":"137332630","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"400000","maxPositionSize":"22000000","baselinePositionSize":"2180000","assetResolution":"100000","syntheticAssetId":"0x444f47452d35000000000000000000"},"ATOM-USD":{"market":"ATOM-USD","status":"ONLINE","baseAsset":"ATOM","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.01","indexPrice":"28.4932","oraclePrice":"28.5340","priceChange24H":"-2.035984","nextFundingRate":"-0.0000487751","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"24370439.887000","trades24H":"9426","openInterest":"1104803.0","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"3000","maxPositionSize":"158000","baselinePositionSize":"16000","assetResolution":"10000000","syntheticAssetId":"0x41544f4d2d37000000000000000000"},"ZRX-USD":{"market":"ZRX-USD","status":"ONLINE","baseAsset":"ZRX","quoteAsset":"USD","stepSize":"1","tickSize":"0.001","indexPrice":"0.6598","oraclePrice":"0.6592","priceChange24H":"-0.048451","nextFundingRate":"-0.0000070338","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"10","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"12594556.282000","trades24H":"4099","openInterest":"11586619","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"100000","maxPositionSize":"5000000","baselinePositionSize":"500000","assetResolution":"1000000","syntheticAssetId":"0x5a52582d3600000000000000000000"},"SOL-USD":{"market":"SOL-USD","status":"ONLINE","baseAsset":"SOL","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.001","indexPrice":"104.7960","oraclePrice":"104.9100","priceChange24H":"-8.894022","nextFundingRate":"-0.0000309724","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"54186410.727700","trades24H":"18151","openInterest":"436082.0","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"700","maxPositionSize":"34900","baselinePositionSize":"3400","assetResolution":"10000000","syntheticAssetId":"0x534f4c2d3700000000000000000000"},"UMA-USD":{"market":"UMA-USD","status":"ONLINE","baseAsset":"UMA","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.01","indexPrice":"6.1678","oraclePrice":"6.1647","priceChange24H":"-0.452454","nextFundingRate":"-0.0000293797","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"4689780.373000","trades24H":"4477","openInterest":"281698.9","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"1000","maxPositionSize":"30000","baselinePositionSize":"2000","assetResolution":"10000000","syntheticAssetId":"0x554d412d3700000000000000000000"},"AAVE-USD":{"market":"AAVE-USD","status":"ONLINE","baseAsset":"AAVE","quoteAsset":"USD","stepSize":"0.01","tickSize":"0.01","indexPrice":"173.6709","oraclePrice":"173.2700","priceChange24H":"-13.491902","nextFundingRate":"-0.0000076472","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"6094287.667100","trades24H":"1984","openInterest":"87170.52","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"300","maxPositionSize":"17000","baselinePositionSize":"1700","assetResolution":"100000000","syntheticAssetId":"0x414156452d38000000000000000000"},"ADA-USD":{"market":"ADA-USD","status":"ONLINE","baseAsset":"ADA","quoteAsset":"USD","stepSize":"1","tickSize":"0.001","indexPrice":"1.1307","oraclePrice":"1.1290","priceChange24H":"-0.057525","nextFundingRate":"-0.0000056476","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"10","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"8670745.789000","trades24H":"3557","openInterest":"17945971","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"46000","maxPositionSize":"2300000","baselinePositionSize":"230000","assetResolution":"1000000","syntheticAssetId":"0x4144412d3600000000000000000000"},"SNX-USD":{"market":"SNX-USD","status":"ONLINE","baseAsset":"SNX","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.01","indexPrice":"5.1717","oraclePrice":"5.1720","priceChange24H":"-0.623267","nextFundingRate":"0.0000052792","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"4324102.723000","trades24H":"2399","openInterest":"2694507.9","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"11000","maxPositionSize":"520000","baselinePositionSize":"52000","assetResolution":"10000000","syntheticAssetId":"0x534e582d3700000000000000000000"},"FIL-USD":{"market":"FIL-USD","status":"ONLINE","baseAsset":"FIL","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.01","indexPrice":"22.7821","oraclePrice":"22.7500","priceChange24H":"-1.163894","nextFundingRate":"-0.0000161504","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"6352160.834000","trades24H":"3903","openInterest":"478499.1","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"1400","maxPositionSize":"68000","baselinePositionSize":"6800","assetResolution":"10000000","syntheticAssetId":"0x46494c2d3700000000000000000000"},"ZEC-USD":{"market":"ZEC-USD","status":"ONLINE","baseAsset":"ZEC","quoteAsset":"USD","stepSize":"0.01","tickSize":"0.1","indexPrice":"122.0400","oraclePrice":"121.7926","priceChange24H":"-4.200376","nextFundingRate":"0.0000006253","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"3243018.921000","trades24H":"2368","openInterest":"55010.85","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"100","maxPositionSize":"3000","baselinePositionSize":"200","assetResolution":"100000000","syntheticAssetId":"0x5a45432d3800000000000000000000"},"YFI-USD":{"market":"YFI-USD","status":"ONLINE","baseAsset":"YFI","quoteAsset":"USD","stepSize":"0.0001","tickSize":"1","indexPrice":"24236.5076","oraclePrice":"24199.5000","priceChange24H":"-1797.362365","nextFundingRate":"-0.0000064895","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.001","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"4466618.461300","trades24H":"2223","openInterest":"744.6725","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"3","maxPositionSize":"140","baselinePositionSize":"14","assetResolution":"10000000000","syntheticAssetId":"0x5946492d3130000000000000000000"},"LINK-USD":{"market":"LINK-USD","status":"ONLINE","baseAsset":"LINK","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.001","indexPrice":"17.2721","oraclePrice":"17.2700","priceChange24H":"-1.217733","nextFundingRate":"-0.0000145151","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"7246391.294400","trades24H":"3673","openInterest":"1087769.4","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"3900","maxPositionSize":"200000","baselinePositionSize":"20000","assetResolution":"10000000","syntheticAssetId":"0x4c494e4b2d37000000000000000000"},"DOT-USD":{"market":"DOT-USD","status":"ONLINE","baseAsset":"DOT","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.01","indexPrice":"20.2224","oraclePrice":"20.1624","priceChange24H":"-1.618407","nextFundingRate":"-0.0000241039","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"9136465.054000","trades24H":"6092","openInterest":"1561849.2","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"2900","maxPositionSize":"150000","baselinePositionSize":"14600","assetResolution":"10000000","syntheticAssetId":"0x444f542d3700000000000000000000"},"MATIC-USD":{"market":"MATIC-USD","status":"ONLINE","baseAsset":"MATIC","quoteAsset":"USD","stepSize":"1","tickSize":"0.001","indexPrice":"1.8393","oraclePrice":"1.8368","priceChange24H":"-0.188705","nextFundingRate":"-0.0000233629","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"10","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"36449333.021000","trades24H":"11703","openInterest":"18980542","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"80000","maxPositionSize":"4000000","baselinePositionSize":"410000","assetResolution":"1000000","syntheticAssetId":"0x4d415449432d360000000000000000"}}}
        
    try:
        global ftx_funds
        ftx_funds = [
            requests.get("https://ftx.com/api/futures/%s-PERP/stats" % x).json()
            for x in ASSETS
        ]

        global ftx_px
        ftx_px = [
        requests.get("https://ftx.com/api/futures/%s-PERP" % x).json()
            for x in ASSETS

        ]
    except:
        ftx_funds = [{
            "success": False,
            "result": {
                "volume": np.nan,
                "nextFundingRate": np.nan,
                "nextFundingTime": "2021-12-03T21:00:00+00:00",
                "openInterest": np.nan,
            },
        }]*len(ASSETS)

        ftx_px = [{"success":False,
        "result":{"name":"AVAX-PERP","underlying":np.nan, "description":"Avalanche Perpetual Futures",
        "type":"perpetual","expiry":True,"perpetual":True,"expired":False,"enabled":False,
        "postOnly":False,"priceIncrement":0.001,"sizeIncrement":0.1,"last":84.491,"bid":84.498,
        "ask":84.531,"index":np.nan,"mark":np.nan,"imfFactor":0.002,"lowerBound":80.257,"upperBound":88.733,
        "underlyingDescription":"Avalanche","expiryDescription":"Perpetual","moveStart":None,
        "marginPrice":84.535,"positionLimitWeight":100.0,"group":"perpetual","change1h":-0.013858591043243936,
        "change24h":-0.07248110071208347,"changeBod":np.nan,"volumeUsd24h":212413536.68,
        "volume":np.nan,"openInterest":np.nan,"openInterestUsd":np.nan}}] * len(ASSETS)

    dydx_assets = list(dydx_data['markets'].keys())

    ftx_fund_rate = [z["result"]["nextFundingRate"] for z in ftx_funds]
    ftx_oi = [z["result"]["openInterest"] for z in ftx_funds]

    dydx_data_assets = [dydx_data['markets'][ast+'-USD'] if ast+'-USD' in dydx_data['markets'] else {} for ast in ASSETS ]

    dydx_fund_rate = [float(dydx_dat.get('nextFundingRate',np.nan)) for dydx_dat in dydx_data_assets]
    dydx_volume = [float(dydx_dat.get('volume24H',np.nan)) for dydx_dat in dydx_data_assets]
    dydx_oi = [float(dydx_dat.get('openInterest', np.nan)) for dydx_dat in dydx_data_assets]

    drift_m_sum = drift.T

    drift_fund_rate = (
        (drift_m_sum["last_mark_price_twap"].astype(float) - drift_m_sum["last_oracle_price_twap"].astype(float))
        / drift_m_sum["last_oracle_price_twap"].astype(float)
    ) / 24

    drift_oi = (drift_m_sum['base_asset_amount_long'].astype(float) - drift_m_sum['base_asset_amount_short'].astype(float))
    print('FUNDING_SCALE', FUNDING_SCALE)
    funding_rate_df = pd.concat(
        [pd.Series(ftx_fund_rate), pd.Series(dydx_fund_rate), pd.Series(mango_fund_rate), drift_fund_rate], axis=1
    ).T #* FUNDING_SCALE
    funding_rate_df.index = ["(FTX)", "DYDX", "Mango", "Drift"]
    funding_rate_df.index.name = "Protocol"
    funding_rate_df.columns = ASSETS
    funding_rate_df = funding_rate_df * 100
    for col in funding_rate_df.columns:
        funding_rate_df[col] = funding_rate_df[col].map("{:,.5f}%".format).replace('nan%','')

    # funding_rate_df = funding_rate_df.reset_index()

    # make volume table too
    bonfida_markets = {
        "BTC": "475P8ZX3NrzyEMJSFHt9KCMjPpWBWGa6oNxkWcwww2BR",
        "SOL": "jeVdn6rxFPLpCH9E6jmk39NTNx2zgTmKiVXBDiApXaV",
        "ETH": "3ds9ZtmQfHED17tXShfC1xEsZcfCvmT8huNG79wa4MHg",
    }

    drift_markets = {v: str(k) for k,v in MARKET_INDEX_TO_PERP.items()}
    try:
        fida_volume = [
            requests.get(
                "https://serum-api.bonfida.com/perps/volume?market=%s"
                % bonfida_markets[x]
            ).json()["data"]["volume"]
            for x in ("SOL", "BTC", "ETH")
        ]
    except:
        fida_volume = [np.nan] * len(ASSETS)

    mango_volume = [np.nan]*len(ASSETS)
    for i,x in enumerate(ASSETS):
        try:
            mango_volume[i] = requests.get(
                "https://event-history-api.herokuapp.com/stats/perps/%s"
                % mango_markets[x]
            ).json()["data"]["volume"] 
        except:
            pass
            
    drift_volume = [np.nan]*len(ASSETS)
    for i,x in enumerate(ASSETS):
        try:
            drift_volume[i] = requests.get(
            "https://mainnet-beta.api.drift.trade/stats/24HourVolume?marketIndex=%s"
            % drift_markets[x+'-PERP']
        ).json()["data"]["volume"]
        except:
            pass

    # ftx_volume = [z["result"]["volume"] for z in ftx_funds]
    ftx_volume = [z["result"]["volumeUsd24h"] for z in ftx_px]

    oi = pd.concat(
        [pd.Series(ftx_oi), pd.Series(dydx_oi), pd.Series(mango_oi), drift_oi], axis=1
    ).T
    oi.index = [
            "(FTX)",
            "DYDX",
            "Mango",
            "Drift"
        ]
    for col in oi.columns:
        oi[col] = oi[col].astype(float).map("{:,.1f}".format)
    oi = oi.replace('nan','')
    oi.index.name = 'Protocol'
    oi.columns = list(ASSETS)

    volumes = pd.DataFrame(
        [ftx_volume, dydx_volume, mango_volume, drift_volume, fida_volume],
        index=[
            "(FTX)",
            "DYDX",
            "Mango",
            "Drift",
            "Bonfida",
        ],
    )
    # volumes.iloc[[0], :] *= np.array([[140, 42000, 3600, 66, 84, 520, 2.13]])  # todo lol
    for col in volumes.columns:
        volumes[col] = volumes[col].astype(float).map("${:,.0f}".format).replace('$nan','')
    # volumes = volumes.reset_index()
    volumes.index.name = "Protocol"
    volumes.columns = list(ASSETS)
    # volumes

    return funding_rate_df, volumes, oi, ftx_px

def get_mango_prices(market):
    mango_symbol_to_market = {
        "BTC": "DtEcjPLyD4YtTBB4q8xwFZ9q49W89xZCZtJyrGebi5t8",
        "SOL": "2TgaaVoHgnSeEtXvWTx13zQeTf4hYWAMEiMQdcG6EwHi",
        "ETH": "DVXWg6mfwFvHQbGyaHke4h3LE9pSkgbooDSDgA4JBC8d",
        "LUNA": "BCJrpvsB2BJtqiDgKVC4N6gyX1y24Jz96C6wMraYmXss",
        "AVAX": "EAC7jtzsoQwCbXj1M3DapWrNLnc3MBwXAarvWDPr2ZV9",
        "BNB": "CqxX2QupYiYafBSbA519j4vRVxxecidbh2zwX66Lmqem",
        'SRM': "4GkJj2znAr2pE2PBbak66E12zjCs2jkmeafiJwDVM9Au",
        'RAY': "DtEcjPLyD4YtTBB4q8xwFZ9q49W89xZCZtJyrGebi5t8",
        'MNGO': "DtEcjPLyD4YtTBB4q8xwFZ9q49W89xZCZtJyrGebi5t8",
        'ADA': "Bh9UENAncoTEwE7NDim8CdeM1GPvw6xAT4Sih2rKVmWB",
        'FTT': "AhgEayEGNw46ALHuC5ASsKyfsJzAm5JY8DWqpGMQhcGC",
    }

    addy = mango_symbol_to_market.get(market.split('-')[0])
    if addy is not None:
        mango_sol_candles = requests.get(
            "https://event-history-api-candles.herokuapp.com/trades/address/%s" % addy
        ).json()["data"]

        return mango_sol_candles
    else:
        return None
   


def get_fida_prices():
    try:
        mango_sol_candles = requests.get(
            "https://serum-api.bonfida.com/perps/trades?market=jeVdn6rxFPLpCH9E6jmk39NTNx2zgTmKiVXBDiApXaV"
        ).json()["data"]
        mango_btc_candles = requests.get(
            "https://serum-api.bonfida.com/perps/trades?market=475P8ZX3NrzyEMJSFHt9KCMjPpWBWGa6oNxkWcwww2BR"
        ).json()["data"]
        mango_eth_candles = requests.get(
            "https://serum-api.bonfida.com/perps/trades?market=3ds9ZtmQfHED17tXShfC1xEsZcfCvmT8huNG79wa4MHg"
        ).json()["data"]
        return [mango_sol_candles, mango_btc_candles, mango_eth_candles]+[[{"markPrice": np.nan, "time": 0}] * 2] * 17
    except:
        return [[{"markPrice": np.nan, "time": 0}] * 2] * 15


def mango_py():
    context = mango.ContextBuilder.build(cluster_name="mainnet")
    return context

def load_mango_data(market="SOL-PERP"):
    # Find the addresses associated with the Perp market
    # perp_stub = context.market_lookup.find_by_symbol("perp:" + market)

    # Load the rest of the on-chain metadata of the market
    perp_market = mango.market(context, market)
    # z = perp_market.fetch_funding(context)
    return perp_market

context = mango_py()
# MARKET = "SOL-PERP"

"""
# Platyperps
"""


# with st.echo():

ROOT = "https://raw.githubusercontent.com/0xbigz/drift-flat-data/main/data/"

msum = ROOT + 'markets_state.csv'
drift_market_summary = pd.read_csv(msum, index_col=[0])
drift_market_summary.columns = [int(x) for x in drift_market_summary.columns]

tab = st.sidebar.radio(
    "PlatyPerps",
    ('Overview', 'Price', 'Liquidity', 'About', 'Drift', 'Mango'))

if tab == 'Overview':
    # st.table(drift_market_summary)
    funding_rate_df, volumes, oi, ftx_px = make_funding_table(drift_market_summary)
    st.table(funding_rate_df)
    st.table(volumes)
    st.table(oi)

if tab not in ['About', 'Overview']:
    MARKET = st.selectbox("Select a Market:", MARKET_INDEX_TO_PERP.values())
    market_index = MARKET_PERP_TO_INDEX[MARKET]
    st.text(MARKET + ' (market_index='+str(market_index)+') selected')
    df = drift_market_summary[market_index]
    # MARKET = df.loc['market_name']
    base_asset_reserve = float(df.loc['base_asset_reserve'])
    mark_price = float(df.loc['mark_price'])

if tab == 'Drift':
    st.table(df)


    # mango_book = perp_market.fetch_orderbook(context)

    # st.table(pd.DataFrame({'spread': mango_book.spread,
    #                 'price': mango_book.mid_price
    # }, index=[MARKET]))

if tab == 'Price':
    ff = ROOT + 'trade_history.csv'
    df = pd.read_csv(ff, parse_dates=[0])
    df2 = (df.pivot_table(columns='market_index', index='ts')/1e10)#.ffill()#.head(100)
    df2 = df2.swaplevel(axis=1)
    df2m = df2[market_index].dropna()
    # df2m.index += datetime.timedelta(hours=5)

    # fig = px.line(df2m, title='trades')
# st.table(df2m.head(10))
# st.plotly_chart(fig)

    mango_price_data = get_mango_prices(MARKET)

    if mango_price_data is not None:
        mprices = pd.DataFrame(mango_price_data).set_index('time')
        mprices['size'] *= mprices['side'].apply(lambda x: -1 if x=='sell' else 1)
        mprices.index = pd.to_datetime(mprices.index*int(1e6))
        mprices2 = mprices[['price','size']]
        mprices2.index = mprices2.index.tz_localize('UTC')
        
        mprices2 = mprices2.reset_index().drop_duplicates(subset='time').set_index('time')
    else:
        mprices2 = pd.concat({'price': df2m['mark_price_after']*np.nan},axis=1)

    drifting_mango = pd.concat({
        'drift': df2m['mark_price_after'] , 
        'mango': mprices2['price'],
        'oracle': df2m['oracle_price']
    },axis=1).ffill()

    # st.table(mprices2)

    fig = px.line(drifting_mango, title=MARKET+' price (trades)')
    st.plotly_chart(fig)


if tab == 'Mango':
    mango_price_data = get_mango_prices(MARKET)

    if mango_price_data is not None:
        perp_market = load_mango_data(MARKET)
        mango_fund = perp_market.fetch_funding(context)
        st.table(pd.DataFrame([mango_fund]))



# trade_amount = st.number_input(label="Buy "+MARKET)
if tab == 'Liquidity':
    mango_price_data = get_mango_prices(MARKET)

    if mango_price_data is not None:
        perp_market = load_mango_data(MARKET)

        mango_book = perp_market.fetch_orderbook(context)

        m_bids = pd.DataFrame([(float(x.price), float(x.quantity)) for x in mango_book.bids])\
            .groupby(0).sum()\
            .sort_index(ascending=False)\
            .cumsum()
        m_asks = pd.DataFrame([(float(x.price), float(x.quantity)) for x in mango_book.asks])\
            .groupby(0).sum().cumsum()


        depth_slide = st.slider("Depth", 1, int(1/.001), 1)
        price_min = float(mango_book.mid_price)*float(1-depth_slide*.001)
        price_max = float(mango_book.mid_price)*float(1+depth_slide*.001)
        # st.table(pd.Series([price_min, price_max]))
        # st.table(m_asks.index)
        m_bids_ = m_bids.loc[:price_min]
        m_bids_.columns = ['bids']
        m_asks_ = m_asks.loc[:price_max]
        m_asks_.columns = ['asks']
        mango_depth = pd.concat([m_bids_, m_asks_]).replace(0, np.nan)

        # st.table(m_bids_)
        # st.table(m_asks_)
        def calc_slip(x):
            f = x/base_asset_reserve
            slippage = 1/(1-f)**2 - 1
            return slippage
        def calc_slip_short(x):
            f = x/base_asset_reserve
            slippage = 1 - 1/(1+f)**2
            return slippage

        max_f = np.sqrt(price_max)/np.sqrt(mark_price) - 1

        # st.table(pd.Series([max_f, mark_price, price_max, base_asset_reserve]))
        quantities_max = max(1, int(max_f*base_asset_reserve))
        quantities = list(range(1, quantities_max, int(max(1, quantities_max/100))))
        drift_asks = pd.DataFrame(quantities, 
        columns=['asks'],
        index=[mark_price*(1+calc_slip(x)) for x in quantities])
        drift_bids = pd.DataFrame(quantities, 
        columns=['bids'],
        index=[mark_price*(1-calc_slip_short(x)) for x in quantities])

        drift_depth = pd.concat([drift_bids, drift_asks]).replace(0, np.nan)

        fig = make_subplots(
            rows=2, cols=1,
             shared_xaxes=True,
            subplot_titles=['drift depth', 'mango depth'])



        # figD = px.line(drift_depth, title=MARKET+' drift depth')
        # figM = px.line(mango_depth, title=MARKET+' mango depth')

        fig.add_trace( go.Scatter(x=drift_depth.index, y=drift_depth['bids']),  row=1, col=1)
        fig.add_trace( go.Scatter(x=drift_depth.index, y=drift_depth['asks']),  row=1, col=1)

        fig.add_trace( go.Scatter(x=mango_depth.index, y=mango_depth['bids']),  row=2, col=1)
        fig.add_trace( go.Scatter(x=mango_depth.index, y=mango_depth['asks']),  row=2, col=1)


        st.plotly_chart(fig)
        # st.plotly_chart(figM)


        # st.table(pd.DataFrame(
        #     {'drift': [calc_slip(1)*100, .1], 'mango': [0, .05]}
        # , index=['slippage', 'fee']))

        # st.plotly_chart(fig)
        # st.table()

if tab == 'About':
    st.markdown('follow us [@platyperps](https://twitter.com/@platyperps)')
    st.text('high rollers: feel free to donate :3 any SPL tokens to') 
    st.markdown('[pLaTMYUZVTzAmpc73NWkhHVJ3YKAq8FEHvHmuqKjdPh](https://solscan.io/account/pLaTMYUZVTzAmpc73NWkhHVJ3YKAq8FEHvHmuqKjdPh)')

    st.text(
        """
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    ;cldxOKNWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
        ..,cox0NWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    kdoc:,..    .':d0NMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMWX0koc,.   .,lkXWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMWKkl'.   .:dKWMMMMMMMMMMMMMMMMMWNKOkxddoodxkOKNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMNOo;.   .,lkXWMMMMMMMMWNKko;'.           .':oONMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMMWKxc'    .;lxkxdolc;'.    .,;:cllllc;'.    'o0WMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMMMMMWNOo;.            .':okKNWMMMMMMMWNKkl,.  .cKWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMWXOdl:::clldxOKNWMMMMMMMMMMMMMMMMMNk:.  .kWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNd.  ,KMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNX0kkKWMMMMMM0'   ,kNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWo..  .kMMMMMMO.     ,dKWMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMW0ol::oKMMMMMMx.  ..   .;lk0XWWWWNKOkxxk0NMMMMMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWo   oXkc.    ..',;,'.      'lKMMMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMX:  .kMMWXko:,..    ..';::,.  'kWMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM0'  ,KMMMMMMMWXK0OOO0XNWMMNx.  '0MMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMx.  cNMMMMMMMMMMMMMMMMMMMMW0,  .kMMMMMM
    MMMMMMMMMMMMWKdoONMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNc  .xMMMMMMMMMMMMMMMMMMWXOl.   lXMMMMMM
    MMMMMMMMMMWMWl  .cKMMMMMMMMMMMMMMWKKWMMMMMMMMMMMMMMMMMMMMMWXl.  .dXNMMMMMMMMMMWNXOxo:'.   ,xNMMMMMMM
    MMMMMMMMMMMMMKc   'kWMMMMMMMMMMMNo..,oONWMMMMMMMMMMMMMMMNOl.     ..';:clllllc:;'.     .,lONMMMMMMMMM
    MMMMMMMMMMMMMMNx.  .oXMMMMMMMMMMWk,.   ':ok0XNNNNXXK0ko:'   .;lc,..             ..;cokXWMMMMMMMMMMMM
    MMMMMMMMMMMMMMMW0;   ;0WMMMMMMMMMMNk,      ..''''...     .;oONMMWNKOkxddoooddxkOKNWMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMXo.  .xWMMMMMMMMMMK,     ..........';cokKWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMWWk.  .lNMMMMMMMMMNk;.    .',:lx0KXNWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    WWNNNXXXK00Okxdolc:;.    lNMMMMMMMMMMW0dc,.     .lkKWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    '''''.....           .   .xWMMMMMMMMMMMMMWXOdl,    cNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    .........',,;:clodxkO0x.  .oXWMMMMMMMMMMMMMMWM0'   ,KMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    000KKKXXNNWWMMMMMMMMMMWO,   .:loxO0KXNWWMWWWXKo.   :XMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMXd;.      ...'',,;,'..   .:kWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMWKOxoc:,'...      ..';o0NWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWNXK00OOOOO0XNWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM""")