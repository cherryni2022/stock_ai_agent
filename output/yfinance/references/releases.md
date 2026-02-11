# Releases

Version history for this repository (105 releases).

## 1.1.0: 1.1.0
**Published:** 2026-01-24

Price repair:
- new: fix capital-gains double-counting
- fewer stock-split false positives

Various small fixes.

Full changelog #2682

Thanks @salsugair @kbluck @orionnelson @ctasada 

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/1.1.0)

---

## 1.0: 1.0
**Published:** 2025-12-22

yfinance been stable a long time now, time to graduate to version 1.0 🎉 

No breaking changes, but some deprecation warnings for the new config method https://ranaroussi.github.io/yfinance/advanced/config.html

Various fixes.

Thanks @ianmihura @axisrow @danchev @biplavbarua @ericpien @evanreynolds9 

Full changelog #2637

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/1.0)

---

## 0.2.66: 0.2.66
**Published:** 2025-09-17

Screener: add Swiss exchange and industry field

Support MIC #2579

Fixes:
- parse epoch dt #2573
- earnings_dates #2591
- merge intraday prices with divs/splits #2595
- exceptions missing detail #2599

Thanks @mxdev88 @jdmcclain47 @hjlgood @Phil997 

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.66)

---

## 0.2.65: 0.2.65
**Published:** 2025-07-06

- Prices: fix handling arguments `start/end/period`
- Financials: ensure dtype float
- Price repair: update metadata when changing FX

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.65)

---

## 0.2.64: 0.2.64
**Published:** 2025-06-27

`earnings_dates`: new column `Event Type`  #2555

Prices fixes:
- handle dividends with currency  #2549
- handle `period` when `start/end` also set  #2550

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.64)

---

## 0.2.63: 0.2.63
**Published:** 2025-06-12

Fix `download()`+ISIN

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.63)

---

## 0.2.62: 0.2.62
**Published:** 2025-06-08

- Improve "proxy deprecated" messaging.
- Fix ISIN+proxy. New ISIN cache.
- Fix prices `period=max`.

Thanks @cole-st-john 

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.62)

---

## 0.2.61: 0.2.61
**Published:** 2025-05-12

Fix ALL type hints in websocket #2493

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.61)

---

## 0.2.60: 0.2.60
**Published:** 2025-05-11

Big fixes:
- cookie reuse, DNS blocking cookie fetch #2483
- protobuf & websocket #2485 #2488

Little fixes:
- predefined screen + `offset` #2440
- deprecate `requests` #2487

Thanks @dhruvan2006 

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.60)

---

## 0.2.59: 0.2.59
**Published:** 2025-05-07

Stop overriding `curl_cffi` user-agent - helps with rate-limit #2450

**EDIT: new feature: [live data via websocket](https://ranaroussi.github.io/yfinance/reference/yfinance.websocket.html)** - forgot to announce

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.59)

---

## 0.2.58: 0.2.58
**Published:** 2025-05-02

Fixes:
- switch to `curl_cffi` session to fix false rate-limit errors #2430 [ [reason = TLS fingerprinting](https://github.com/ranaroussi/yfinance/issues/2422#issuecomment-2840759533) ]
- predefined screen arg count/size #2425

Thanks @bretsky @R5dan 

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.58)

---

## 0.2.57: 0.2.57
**Published:** 2025-04-28

Fix proxy msg & pass-through #2418

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.57)

---

## 0.2.56: 0.2.56
**Published:** 2025-04-23

Features:
- `yf.Lookup`
- `yf.set_config()`

Fixes: `info` fetch, ISIN, prices missing last row, prices NonExistentTimeError

Full changelog #2410

Thanks @dhruvan2006  @JanMkl 


[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.56)

---

## 0.2.55: 0.2.55
**Published:** 2025-03-20

New feature: fetch TTM financials

Fixes:
- earnings dates
- price repair
- info IndexError
- get_splits|dividends|capital_gains

Thanks @JanMkl @dhruvan2006

Full changelog: #2372

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.55)

---

## 0.2.54: 0.2.54
**Published:** 2025-02-18

Hotfix fetch error #2277 thanks @dhruvan2006 

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.54)

---

## 0.2.53: 0.2.53
**Published:** 2025-02-15

Main changes:
- fixes for `Ticker.*_holders`
- add pre- and post-market data to `Ticker.info`
- improve prices dividend repair

Thanks @dhruvan2006 @R5dan @ocp1006 

Full changelog #2264

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.53)

---

## 0.2.52: 0.2.52
**Published:** 2025-01-18

Features:
- Improve Screener & docs #2207
- Add `yf.Market` summary & status #2175
- Support custom period in `Ticker.history` #2192
- raise `YfRateLimitError` if rate limited #2108
- add more options to `yf.Search` #2191

Fixes:
- remove hardcoded keys in Analysis #2194
- handle Yahoo changed Search response #2202

Thanks @dhruvan2006 and @R5dan 

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.52)

---

## 0.2.51: 0.2.51
**Published:** 2024-12-19

Features:
- add `yf.Search` #2160
- improve `yf.Screener` and `Ticker.get_news()` #2168 #2173

Fixes and tweaks:
- Fix `Ticker.get_earnings_dates` #2169
- Change `download` argument `auto_adjust` to default True, to match `Ticker.history` #2147

Thanks @hjlgood @ericpien @dhruvan2006 

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.51)

---

## 0.2.50: 0.2.50
**Published:** 2024-11-19

Fixes:
- price repair #2111 #2139
- `download()` index #2109
- `isin()` error #2099
- `growth_estimates` #2127

New documentation website: https://ranaroussi.github.io/yfinance/index.html

Thanks @ericpien @DamienDuv 

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.50)

---

## 0.2.49: 0.2.49
**Published:** 2024-11-10

Fix prices-clean rarely discarding good data #2122

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.49)

---

## 0.2.48: 0.2.48
**Published:** 2024-10-25

Addresses #2100.

Added `multi_level_index` parameter to multi.py with a default value to `True`. If set to `False` and only one ticker is requested - the returned DataFrame will be single-level-index

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.48)

---

## 0.2.47: 0.2.47
**Published:** 2024-10-25

Refactor multi.py to return single-level index when a single ticker is requested

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.47)

---

## 0.2.46: 0.2.46
**Published:** 2024-10-21

Fix regression in 0.2.45 #2094 - thanks @FX196 

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.46)

---

## 0.2.45: 0.2.45
**Published:** 2024-10-20

Feature: `yf.Screener` and `yf.EquityQuery` #2066 

Fixes:
- `history()` IndexError and `download()` KeyError #2068 #2087
- improve dividend repair #2090

Full changelog: #2091

Contributors: @ericpien @antoniouaa @algonell @marco-carvalho

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.45)

---

## 0.2.44: 0.2.44
**Published:** 2024-09-30

Features:
- `yf.Ticker(X).funds_data` #2041
- `yf.Sector(Y)` and `yf.Industry(Z)` #2058

Thanks @ericpien!

Fix: improve dividend repair #2062

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.44)

---

## 0.2.43: 0.2.43
**Published:** 2024-08-24

Fix price-repair bug introduced in 0.2.42 #2036

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.43)

---

## 0.2.42: 0.2.42
**Published:** 2024-08-22

Features:
- fetch SEC filings & analysis
- price repair extended to dividends & adjust

Fix fetch errors for: options, holders, download, news

Full changelog: #2034

Contributors: @Fidasek009 @aaron-jencks @stevenbischoff @ericpien @mreiche

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.42)

---

## 0.2.41: 0.2.41
**Published:** 2024-07-19

Improvements:
- add some missing keys to financials
- new: `Ticker.sustainability`
- prices fetch: fixes, Pandas warnings, and improve repair
- deprecate `Ticker.earnings` RIP

Full changelog: #1971

Contributors: @MohamedAlaa201 @vittoboa @SnowCheetos @rhwvu @lp177

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.41)

---

## 0.2.40: 0.2.40
**Published:** 2024-05-19

Fix typo in 0.2.39 #1942 

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.40)

---

## 0.2.39: 0.2.39
**Published:** 2024-05-19

Maintenance + price repair improvements. Details in #1927

Thanks @vittoboa @elibroftw @marcofognog 

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.39)

---

## 0.2.38: 0.2.38
**Published:** 2024-04-16

Fix holders and insiders #1908 - thanks @vittoboa

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.38)

---

## 0.2.37: 0.2.37
**Published:** 2024-02-25

Small fixes:
- Fix Pandas warnings #1838 #1844
- Fix price repair bug, typos, refactor #1866 #1865 #1849
- Stop disabling logging #1841

Thanks @mreiche @Rogach @power-edge @cottrell 

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.37)

---

## 0.2.36: 0.2.36
**Published:** 2024-01-21

Small fixes:
- Name `download()` column levels  #1795 
- Fix `history(keepna=False)` when `repair=True`  #1824 
- Handle `peewee` with old `sqlite`  #1827 
- Minor: #1724 #1823 #1830 #1833

Thanks: @mreiche @amanlai @molpcs @ange-daumal 

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.36)

---

## 0.2.35: 0.2.35
**Published:** 2024-01-07

Fixes for 0.2.34: fix behaviour with invalid symbols & unit tests #1816

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.35)

---

## 0.2.34: 0.2.34
**Published:** 2024-01-06

Lots of changes here, thanks everyone.

Features:
- Add Recommendations Trend Summary #1754 @bot-unit
- Add Recommendation upgrades & downgrades #1773 @bot-unit
- Add Insider Roster & Transactions #1772 @JuliaLWang8
- Moved `download()` progress bar to STDERR #1776 @coskos-ops
- PIP optional dependencies #1771 #1807 @JuliaLWang8

Fixes
- Fix `download()` `DatetimeIndex` on invalid symbols #1779 @VishnuAkundi
- Price repair fixes #1768 #1798
- Fix `Ticker.calendar` fetch #1790 @bot-unit
- Fix invalid date entering cache DB #1796
- Fixed adding complementary to `Ticker.info` #1774 @coskos-ops
- Fix `raise_errors` argument ignored in `Ticker.history()` #1806 @puntonim
- `Ticker.earnings_dates`: fix warning `Value 'NaN' has dtype incompatible with float64` #1810 @Tejasweee

Maintenance
- Refactor Ticker proxy #1711 @rickturner2001
- Add Ruff linter checks #1756 @marco-carvalho
- Resolve Pandas FutureWarnings #1766 @JuliaLWang8

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.34)

---

## 0.2.33: 0.2.33
**Published:** 2023-12-06

Cookie fixes:
- fix backup strategy #1759 
- fix `Ticker(ISIN)` #1760  - thanks @bot-unit

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.33)

---

## 0.2.32: 0.2.32
**Published:** 2023-11-18

Add cookie & crumb to requests, fix various HTTP errors. #1657 
Thanks for big help from:
@bot-unit
@psychoz971
@JShen123

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.32)

---

## 0.2.31: 0.2.31
**Published:** 2023-10-04

Fix TZ cache exception blocking import #1705 #1709
Fix merging pre-market events with intraday prices #1703

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.31)

---

## 0.2.31b2: 0.2.31b2
**Published:** 2023-10-01
**Pre-release**

## What's Changed
* Finish TZ cache lazy-load #1709

**Full Changelog**: https://github.com/ranaroussi/yfinance/compare/0.2.31b1...0.2.31b2

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.31b2)

---

## 0.2.31b1: 0.2.31b1
**Published:** 2023-10-01
**Pre-release**

## What's Changed
* Fix merging pre-market events with intraday prices #1703
* Fix TZ cache exception blocking import #1705

**Full Changelog**: https://github.com/ranaroussi/yfinance/compare/0.2.30...0.2.31b1

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.31b1)

---

## 0.2.30: 0.2.30
**Published:** 2023-09-24

Fix `OperationalError` #1698

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.30)

---

## 0.2.29: 0.2.29
**Published:** 2023-09-22

Fixes:
- Fix pandas warning when retrieving quotes - thanks @difelice #1672
- Replace sqlite3 with peewee for 100% thread-safety -  #1675
- Fix merging events with intraday prices - #1684
- Fix error when calling enable_debug_mode twice - thanks @arduinocc04 #1687
- Price repair fixes #1688

**Full Changelog**: https://github.com/ranaroussi/yfinance/compare/0.2.28...0.2.29

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.29)

---

## 0.2.28: 0.2.28
**Published:** 2023-08-13

- Fix `TypeError: 'FastInfo' object is not callable` #1636
- Improve & fix price repair #1633 #1660
- `option_chain()` also return underlying data - thanks @DanielGoldfarb #1606

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.28)

---

## 0.2.27: 0.2.27
**Published:** 2023-08-03

Bug fixes:
- fix merging 1d-prices with out-of-range divs/splits #1635
- fix multithread error 'tz already in cache' #1648

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.27)

---

## 0.2.26: 0.2.26
**Published:** 2023-07-21

Proxy improvements
- bug fixes #1371
- security update - thanks @ricardoprins #1625

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.26)

---

## 0.2.25: 0.2.25
**Published:** 2023-07-18

Fix single ISIN as ticker - thanks @ricardoprins #1611
Fix 'Only 100 years allowed' error - thanks @lucas03 #1576

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.25)

---

## 0.2.24: 0.2.24
**Published:** 2023-07-14

Fix info[] missing values #1603

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.24)

---

## 0.2.23: 0.2.23
**Published:** 2023-07-13

Fix 'Unauthorized' error - thanks @signifer-geo #1595

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.23)

---

## 0.2.22: 0.2.22
**Published:** 2023-06-24

 Fix unhandled `sqlite3.DatabaseError` #1574 

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.22)

---

## 0.2.21: 0.2.21
**Published:** 2023-06-21

Main changes:
- fixed the 3 main financials tables - income statement, balance sheet, and cash flow #1568
- price repair improved: fix Yahoo messing up dividend and split adjustments #1543

Minor changes:
- fix `logging` double-printing #1562
- fix merging future dividend/split into prices #1567


[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.21)

---

## 0.2.20: 0.2.20
**Published:** 2023-06-07

Switch to `logging` module - thanks @flaviovs #1423 #1493 #1522 #1541

Price history:
- add `session` argument to `download` - thanks @bveber #1547
- optimise #1514
- fixes #1523
- fix TZ-cache corruption #1528

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.20)

---

## 0.2.19b4: 0.2.19b4
**Published:** 2023-05-25
**Pre-release**

Bugfixes:
* Corrupt tkr-tz-csv halting code #1528
* Faulty `download` logging #1541

Post feedback in Discussion: https://github.com/ranaroussi/yfinance/discussions/1516

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.19b4)

---

## 0.2.19b3: 0.2.19b3
**Published:** 2023-05-11
**Pre-release**

Fixes:
- improve logging messages #1522
- price fixes #1523

Post feedback in Discussion: https://github.com/ranaroussi/yfinance/discussions/1516

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.19b3)

---

## 0.2.19b1: 0.2.19b1
**Published:** 2023-05-04
**Pre-release**

Changes:
- Logging module #1493
- optimise Ticker.history #1514

Feedback wanted on switch to Logging module. See the updated README for howto: https://github.com/ranaroussi/yfinance/tree/dev#logging

Post feedback in Discussion: https://github.com/ranaroussi/yfinance/discussions/1516

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.19b1)

---

## 0.2.18: 0.2.18
**Published:** 2023-04-16

Bug fixes:
- `fast_info` error "_np not found"  #1496
- timezone cache  #1498

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.18)

---

## 0.2.17: 0.2.17
**Published:** 2023-04-10

Fix prices error with Pandas 2.0 - thanks @steven9909 #1488

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.17)

---

## 0.2.16: 0.2.16
**Published:** 2023-04-09

Restore missing `Ticker.info` keys - thanks @kennykos #1480

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.16)

---

## 0.2.14: 0.2.14
**Published:** 2023-03-25

Fix `Ticker.info` dict by fetching from API (also faster than scraping) - thanks @qianyun210603 #1461

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.14)

---

## 0.2.13: 0.2.13
**Published:** 2023-03-21

Price bug fixes:
- fetching big intervals e.g. "3mo" with Capital Gains #1455 (thanks @mppics)
- merging dividends & splits with prices #1452

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.13)

---

## 0.2.12: 0.2.12
**Published:** 2023-02-16

Disable annoying 'backup decrypt' msg 6b8b0d5

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.12)

---

## 0.2.11: 0.2.11
**Published:** 2023-02-10

Fix `history_metadata` accesses for unusual symbols - thanks @sdeibel #1411

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.11)

---

## 0.2.10: 0.2.10
**Published:** 2023-02-07

General:
- fix using sqlite3 < 3.8.2 #1380
- add another backup decrypt option #1379

Prices
- restore original `download()` timezone handling #1385
- fix & improve price repair #1289 2a2928b 86d6acc
- drop intraday intervals if in post-market but `prepost=False` #1311

Info
- `fast_info` improvements:
  - add camelCase keys, add dict functions `values()` & `items()`  #1368
  - fix `fast_info["previousClose"]` #1383
- catch `TypeError` exception #1397

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.10)

---

## 0.2.10b3: 0.2.10b3
**Published:** 2023-02-07
**Pre-release**

- Restore original download() timezone handling #1385
- Price repair bug fix 86d6acccf78432779fad2679e1775962618cdf8b
- Add another backup decrypt option #1379
- Catch TypeError Exception #1397

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.10b3)

---

## 0.2.10b2: 0.2.10b2
**Published:** 2023-02-01
**Pre-release**

Fix parsing `history_metadata['tradingPeriods']` when empty.

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.10b2)

---

## 0.2.10b1: 0.2.10b1
**Published:** 2023-01-31
**Pre-release**

0.2.10 beta 1

Changelog:
- Fix using `sqlite` < 3.8.2 #1380 
- Drop price prepost intervals if `prepost=False` #1311 
- Fix & improve price repair #1289 
- `fast_info` improvements:
  - add camelCase keys, add `dict` functions `values()` & `items()` #1368 
  - fix `fast_info["previousClose"]` #1383

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.10b1)

---

## 0.2.9: 0.2.9
**Published:** 2023-01-26

Fix fast_info bugs #1362

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.9)

---

## 0.2.7: 0.2.7
**Published:** 2023-01-26

- Fix Yahoo decryption, smarter this time #1353
- Rename basic_info -> fast_info #1354

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.7)

---

## 0.2.6: 0.2.6
**Published:** 2023-01-25

Fix Ticker.basic_info lazy-loading #1342

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.6)

---

## 0.2.5: 0.2.5
**Published:** 2023-01-25

- Fix Yahoo data decryption again #1336
- New: Ticker.basic_info - faster Ticker.info #1317

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.5)

---

## 0.2.4: 0.2.4
**Published:** 2023-01-14

- Fix Yahoo data decryption #1297
- New feature: 'Ticker.get_shares_full()' #1301
- Improve caching of financials data #1284
- Restore download() original alignment behaviour #1283
- Fix the database lock error in multithread download #1276

#1302

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.4)

---

## 0.2.3: 0.2.3
**Published:** 2022-12-20

- Make financials API '_' use consistent (e.g. support both balance_sheet and balancesheet)

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.3)

---

## 0.2.2: 0.2.2
**Published:** 2022-12-20

- Restore `financials` attribute (map to `income_stmt`)

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.2)

---

## 0.1.96: 0.1.96
**Published:** 2022-12-20

- Fix info[] not caching for small % of tickers #1258

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.96)

---

## 0.2.1: 0.2.1
**Published:** 2022-12-19

This is a major new release with some new features. The important summary is:
- optimised scraping (thanks @fredrik-corneliusson)
- financials tables match website (thanks @git-shogg
- price data improvements: fix NaN rows, new repair feature, metadata available (see README)

For full list of changes see the pre-release notes:
- [0.2.0rc1](https://github.com/ranaroussi/yfinance/releases/tag/0.2.0rc1)
- [0.2.0rc2](https://github.com/ranaroussi/yfinance/releases/tag/0.2.0rc2)
- [0.2.0rc4](https://github.com/ranaroussi/yfinance/releases/tag/0.2.0rc4)
- [0.2.0rc5](https://github.com/ranaroussi/yfinance/releases/tag/0.2.0rc5)

@ranaroussi Just FYI

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.1)

---

## 0.1.95: 0.1.95
**Published:** 2022-12-19

Fix info[] bug #1257

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.95)

---

## 0.1.94: 0.1.94
**Published:** 2022-12-19

Fix delisted ticker info[] access

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.94)

---

## 0.1.93: 0.1.93
**Published:** 2022-12-18

Fix `Ticker.shares`

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.93)

---

## 0.1.92: 0.1.92
**Published:** 2022-12-18

Decrypt the new Yahoo encryption #1255. Credits to @Rogach for the hard crypto work, and to @fredrik-corneliusson for porting to `cryptography`.

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.92)

---

## 0.2.0rc5: 0.2.0rc5
**Published:** 2022-12-16
**Pre-release**

- Improve financials error handling #1243
- Fix '100x price' repair #1244

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.0rc5)

---

## 0.2.0rc4: 0.2.0rc4
**Published:** 2022-12-13
**Pre-release**

Major changes:

- Access to old financials tables via `get_income_stmt(legacy=True)`
- Optimise scraping financials & fundamentals, 2x faster
- Add 'capital gains' alongside dividends & splits for ETFs, and metadata available via `history_metadata`, plus a bunch of price fixes

For full list of changes see #1238

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.0rc4)

---

## 0.1.90: 0.1.90
**Published:** 2022-12-13

- Restore lxml requirement, increase minimum version #1237

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.90)

---

## 0.1.89: 0.1.89
**Published:** 2022-12-12

- Remove unused incompatible dependency #1222
- Fix minimum Pandas version #1230

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.89)

---

## 0.1.87: 0.1.87
**Published:** 2022-11-16

- Fix localizing midnight when non-existent (DST) #1176
- Fix thread deadlock in bpython #1163

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.87)

---

## 0.1.86: 0.1.86
**Published:** 2022-11-14

- Fix 'trailingPegRatio' #1141
- Improve handling delisted tickers #1142
- Fix corrupt tkr-tz-csv halting code #1162
- Change default start to 1900-01-01 #1170

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.86)

---

## 0.2.0rc2: 0.2.0rc2
**Published:** 2022-11-12
**Pre-release**

### Financials
- fix financials tables to match website  #1128 #1157
- lru_cache to optimise web requests  #1147

### Prices
- improve price repair  #1148
- fix merging dividends/splits with day/week/monthly prices  #1161
- fix the Yahoo DST fixes  #1143
- improve bad/delisted ticker handling  #1140

### Misc
- fix 'trailingPegRatio'  #1138
- improve error handling  #1118

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.0rc2)

---

## 0.1.85: 0.1.85
**Published:** 2022-11-03

Fix info['log_url'] #1062
Fix handling delisted ticker #1137

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.85)

---

## 0.2.0rc1: 0.2.0rc1
**Published:** 2022-10-26
**Pre-release**

Jumping to 0.2 for this big update #1117. 0.1.* will continue to receive bug-fixes
- timezone cache performance massively improved. Thanks @fredrik-corneliusson #1113 #1112 #1109 #1105 #1099
- price repair feature #1110
- fix merging of dividends/splits with prices #1069 #1086 #1102
- fix Yahoo returning latest price interval across 2 rows #1070
- optional: raise price errors as exceptions: `download(..., raise_errors=True)` #1104
- add proper unit tests #1069

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.2.0rc1)

---

## 0.1.84: 0.1.84
**Published:** 2022-10-25

- Make tz-cache thread-safe

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.84)

---

## 0.1.83: 0.1.83
**Published:** 2022-10-25

Reduce spam-effect of tz-fetch

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.83)

---

## 0.1.81: 0.1.81
**Published:** 2022-10-23

Fix unhandled tz-cache exception #1107

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.81)

---

## 0.1.80: 0.1.80
**Published:** 2022-10-22

Fixes:
- `download(ignore_tz=True)` for single ticker #1097
- rare case of error "Cannot infer DST time" #1100

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.80)

---

## 0.1.79: 0.1.79
**Published:** 2022-10-18

Fix when Yahoo returns price=NaNs on dividend day. Dividends were being lost. E.g. ticker "BHP.AX" on 1998-10-30.

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.79)

---

## 0.1.78: 0.1.78
**Published:** 2022-10-18

Fix download() when different timezones #1085

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.78)

---

## 0.1.77: 0.1.77
**Published:** 2022-10-07

Fix user experience bug introduced in 0.1.75 #1076

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.77)

---

## 0.1.75: 0.1.75
**Published:** 2022-10-04

Thanks to @ValueRaider and @asafravid  - we have a new version! 🎉

- [x] The big change is fixing datetime-related issues: #1048 
- [x] add 'keepna' argument #1032 
- [x] speedup Ticker() creation #1042 
- [x] improve a bugfix #1033 

[Discussion](https://github.com/ranaroussi/yfinance/discussions/1074#discussion-4443861)

Huge thank you for @ValueRaider for this one!

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.75)

---

## 0.1.74: 0.1.74
**Published:** 2022-07-11

Fixed bug introduced in 0.1.73

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.74)

---

## 0.1.73: 0.1.73
**Published:** 2022-07-11

Merged several PR that fixed misc issues


[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.73)

---

## 0.1.72: 0.1.72
**Published:** 2022-06-16

bugfix

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.72)

---

## 0.1.71: 0.1.71
**Published:** 2022-06-16

0.1.71
- Added Tickers(…).news()
- Return empty DF if YF missing earnings dates
- Fix EPS % to 0->1
- Fix timezone handling
- Fix handling of missing data
- Clean&format earnings_dates table
- Add ``.get_earnings_dates()`` to retreive earnings calendar
- Added ``.get_earnings_history()`` to fetch earnings data

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.71)

---

## 0.1.70: 0.1.70
**Published:** 2022-01-30

Closes #937.

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.70)

---

## 0.1.69: 0.1.69
**Published:** 2022-01-12

Bug fixed - #920

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.69)

---

## 0.1.68: 0.0.68
**Published:** 2021-12-30


- Fixed `json.decoder.JSONDecodeError` using the latest `requests` library
- Removed official support for Python 3.5 (only) due to lack of support for this version by the `requests` library

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.68)

---

## 0.1.67: 0.1.67
**Published:** 2021-11-20

Added legal disclaimers to make sure people are aware that this library is not affiliated, endorsed, or vetted by Yahoo, Inc.

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.67)

---

## 0.1.66: 0.1.66
**Published:** 2021-11-13

0.1.66
- Merged PR to allow yfinance to be pickled
- Added lookup by ISIN `utils.get_all_by_isin(...)`, `utils.get_ticker_by_isin(...)`, `utils.get_info_by_isin(...)`, `utils.get_news_by_isin(...)`
- `yf.Ticker`, `yf.Tickers`, and `yf.download` will auto-detect ISINs and convert them to tickers
- Propagating timeout parameter through code, setting `request.get(timeout)`
- Adds Ticker.analysis and `Ticker.get_analysis(...)`


[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.66)

---

## 0.1.55: Release 0.1.55
**Published:** 2020-10-05

- fixed institutional holders issue
- other small fixes

[View on GitHub](https://github.com/ranaroussi/yfinance/releases/tag/0.1.55)

---

