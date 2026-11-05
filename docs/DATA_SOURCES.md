# Data Sources and Method Note

Real Estate Project Feasibility and Financial Appraisal Tool. CE725 Team 8, Topic 2. Data Lead: Dinesh Sai (23B1022).
Sources checked on 5 November 2026. Every figure below was looked up on that date; where only a search
summary was seen and the underlying document was not opened, the row says so.

## 1. What the base case represents

The base case is a **mid-segment residential project of 1,00,000 sq ft saleable area in the peripheral
Mumbai Metropolitan Region (MMR)**: the Peripheral Central Suburbs (Kalyan, Dombivli, Ambernath) or
Navi Mumbai's outer nodes (Panvel, Ulwe, Taloja). These are the micro-markets where a selling price of
about ₹7,500 per sq ft is realistic. Knight Frank's H2 2025 report puts the Mumbai-wide average at
₹8,856 per sq ft and records that the Peripheral Central Suburbs took 28% of all Mumbai sales and Navi
Mumbai 17%, so this is where most Mumbai volume actually happens, not an edge case.

The base case was **not** derived from a single real project. The inputs were set first as round, plausible
figures, and then each one was checked against the published range for this market. Where an input sits
outside or at the edge of the published range, section 3 says so and section 4 says what it means for the
result. The team's position is that the tool is a method, the base case is a worked example, and a real
appraisal would replace every input with figures from the specific site.

## 2. Source list

"How seen" records what was actually opened. **Opened** means the document or page was read and the
figure confirmed on the date shown. **Browser needed** means automated tools were refused by the site
(HTTP 403) and a team member must open the link manually before the viva.

| # | Source | Type | Used for | How seen (5 Nov 2026) |
|---|---|---|---|---|
| S1 | Knight Frank Research, *India Real Estate: Office and Residential Market, H2 2025* (PDF, 80 pp.) [link](https://content.knightfrank.com/research/3070/documents/en/india-real-estate-office-and-residential-market-h2-2025-12597.pdf) | Industry research, primary | Selling price, micro-market definitions, sales mix, quarters-to-sell | **Opened.** Mumbai average INR 95,326/sq m (INR 8,856/sq ft), +7% YoY; Peripheral Central Suburbs 28% of H2 2025 sales; QTS 6.4 quarters (PDF pp. 55 to 56) |
| S2 | Locality price pages: Asraa Realty, *Property rates in Dombivli East* (updated 8 Sep 2026) [link](https://asraarealty.com/property-rates/dombivli-east-kalyan/); Square Yards, *Kalyan property rates* (Sep 2026) [link](https://www.squareyards.com/property-rates/kalyan); NoBroker, *Dombivli East locality* (Dec 2025) [link](https://www.nobroker.in/locality-iq/dombivli-east-dombivli-thane-mumbai-liqlt); PropTech Pulse, *Panvel rates* [link](https://www.aurumproptech.in/pulse/tools/rates-and-trends/navi-mumbai/panvel) | Listing portals and brokers | Locality price ranges | **Opened (all four).** Dombivli East asking ₹9,700/sq ft carpet, transaction benchmark ₹8,500, ready reckoner about ₹6,500 built-up; NoBroker range ₹5,405 to 9,542. Kalyan asking ₹9,750, *registered* rate ₹7,900/sq ft over 859 transactions (Nov 2025 to Oct 2026). Panvel average ₹7,835, range ₹5,830 to 9,839. The 99acres page first cited was replaced: it refuses automated access |
| S3 | JLL, *Construction Cost Guide, India 2026* (page dated 22 Mar 2026) [link](https://www.jll.com/en-in/insights/construction-cost-guide-india) | Consultancy guide | Construction cost cross-check | **Opened.** Mumbai high-rise commercial INR 3,900 to 4,900/sq ft; no residential figure given |
| S4 | Infralens, *Construction cost per sq ft in Mumbai* (rates as of 24 Oct 2026) [link](https://infralens.in/prices/mumbai) | Cost-calculator site | Construction cost | **Opened.** Standard ₹3,086/sq ft (materials, labour, basic overheads for RCC frame; excludes professional fees), basic ₹2,407, premium ₹4,166 |
| S5 | JLL India land-transaction data for 2024, reported by Aurum PropTech (13 Mar 2025) [link](https://www.aurumproptech.in/pulse/media/mmrs-unprecendented-land-boom-a-record-breaking-year-for-real-estate-in-2024) and Mumbai Live (12 Mar 2025) [link](https://www.mumbailive.com/en/real-estate/mmr-land-deals-jump-41-in-2024-88064) | Industry research via press | Land cost per acre, MMR | **Opened (both).** MMR: 407 acres in 19 transactions in 2024; per-acre cost rose from about ₹11 crore (2022) to ₹17 crore (2024). The Business Standard and Realty Today pages first cited could not be read |
| S6 | 1acre.in, *Lands and plots for sale in Panvel* [link](https://1acre.in/lands-for-sale/panvel-raigad-maharashtra) | Listing portal | Land asking prices, Panvel | **Opened.** Asking prices ₹3.2 crore/acre (Karnala) to ₹12 crore/acre (Somtane); listings undated beyond "this month" |
| S7 | MCHI-CREDAI, Mayur Shah, *Why real estate development may become unviable due to steep increase in premium and high BMC approval cost* (PDF, 22 pp., 2017 rates) [link](https://www.mchi.net/pdf/Impact_of_RDCR_2034_on_Redevelopment%20by%20Mayur%20Shah.pdf) | Industry body presentation | Approval, marketing and finance cost shares | **Opened.** BMC approval cost 23% to 32% of project cost (average 27%) across suburbs, excluding premium FSI and TDR; marketing 3% to 4%; finance cost 11% |
| S8 | Hariani & Co newsletter, *Fungible compensatory FSI: a step towards transparency* (on the Government of Maharashtra notification of 6 Jan 2012) [link](https://www.hariani.co.in/newsletters/96931_newsletter_april.pdf) | Law-firm note | Fungible FSI rule | **Opened.** Fungible FSI up to 35% residential, 20% industrial and commercial; premium 60% (residential), 80% (industrial), 100% (commercial) of the ready reckoner rate |
| S9 | Reserve Bank of India, *Monetary Policy Statement 2026-27, Resolution of the MPC, 5 to 7 October 2026* (press release 63742) [link](https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=63742) | Regulator, primary | Policy repo rate | **Opened.** Repo rate raised 25 bp to 5.50% on 7 Oct 2026 |
| S10 | Loan Bazaar, *Construction finance* [link](https://loanbazaar.co/loan/construction-finance/) | Lender aggregator | Developer construction-finance rate range | **Opened.** Nationalised banks 10 to 12%, private banks 11 to 13%, NBFC category A 11 to 14%, category B 13 to 17%, AIFs 16 to 20%. Page undated |
| S11 | *Withdrawn.* Business Standard, Feb 2020 article on developer loan rates: paywalled, could not be read by anyone on the team. Not relied on | Press | None | Not usable |
| S12 | ClearTax, *Section 115BAA: new tax rate for domestic companies* [link](https://cleartax.in/s/section-115-baa-tax-rate-domestic-companies) | Tax reference | Corporate tax rate | **Opened.** 22% base + 10% surcharge + 4% cess = 25.168% |
| S13 | EY and NSE, *The Cost of Capital Survey: India Insights 2024* (PDF) [link](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/TheCostofCapitalSurvey_IndiaInsights2024_EY_NSE.pdf) | Survey, primary | Discount rate | **Opened.** Chart 5 (PDF p. 15): real estate 16.4%, overall 14.2%, infrastructure 13.0% |
| S14 | Moorhead, Armitage and Skitmore, *Real estate development feasibility and hurdle rate selection*, Buildings 14(4):1045, 2024 [link](https://www.mdpi.com/2075-5309/14/4/1045) | Peer-reviewed survey of 225 developers in Australia and New Zealand | Hurdle rate practice | **Opened by Dinesh Sai in a browser, 5 Nov 2026.** Section 4.7: developers rely on "a narrow range of MDC (median 20% and standard deviation of 1.41%) and IRR (median 18% and standard deviation 4.85%)". The mean of 18.17% and the 10% to 30% range quoted in search summaries were not checked and are not used |
| S15 | *The Real Estate (Regulation and Development) Act, 2016* (Act 16 of 2016), Gazette copy hosted by UP RERA [link](https://up-rera.in/pdf/reraact.pdf); also India Code [link](https://www.indiacode.nic.in/bitstream/123456789/2158/3/A2016-16.pdf) | Statute, primary | 10% cap before agreement; 70% separate account | **Opened (UP RERA copy).** s.13(1): "A promoter shall not accept a sum more than ten per cent of the cost of the apartment, plot, or building ... as an advance payment or an application fee, from a person without first entering into a written agreement for sale". s.4(2)(l)(D): "seventy per cent. of the amounts realised for the real estate project from the allottees ... shall be deposited in a separate account ... to cover the cost of construction and the land cost" |
| S16 | Two MahaRERA-format payment schedules: Shree Samarth Crown payment slab (developer PDF) [link](https://newprojects.99acres.com/projects/shree_samarth_construction_group/shree_samarth_crown/payplan/kizgse7a.pdf) and a draft MahaRERA agreement for sale, Goregaon East project (2025) [link](https://img.staticmb.com/mbimages/reradoc/2025/06/20/5020009ats_2_4.pdf) | Developer documents | Construction-linked payment pattern | **Opened (both).** 10% before registration, 20% on agreement, 15% at plinth, 5% per slab (or 25% across slabs), then 5% + 5% + 10% + 10% at finishing stages |
| S17 | Realtyhunting, *Property broker commission in India* (updated 6 Oct 2026) [link](https://realtyhunting.com/property-broker-commission-in-india); DNA, *Real estate brokers demand 3-5% from property deals* (15 Jan 2018) [link](https://www.dnaindia.com/mumbai/report-real-estate-brokers-demand-3-5-from-property-deals-2575467/amp) | Brokerage blog and press | Brokerage share | **Opened (both).** Developer channel-partner commission 2% to 5% of base price (up to 6% on stuck inventory), plus 18% GST; 2018 press: brokers demanding 3 to 5%, industry body asking for a 2% minimum |
| S18 | The Construction Index, *L&T bags contract for 24 tower blocks in Bangalore* (28 Mar 2014) [link](https://www.theconstructionindex.co.uk/news/view/landt-bags-contract-for-24-tower-blocks-in-bangalore); Doka reference, *Sky Tower Mumbai*, Parel [link](https://www.doka.com/in/references/show/9070) | Press and supplier reference | Construction duration | **Opened (both).** 24 towers of 18 to 29 storeys on a 42-month schedule (2014); 41-storey, 257 m tower in Parel, 36 months |
| S19 | findcirclerate.com, *Ready reckoner Kalyan* and *Dombivli* (labelled 2026-27) [link](https://findcirclerate.com/india/maharashtra/mumbai/kalyan) | Third-party compilation of IGR rates | Ready reckoner cross-check | **Opened.** Kalyan flat ₹65,000/sq m (₹6,039/sq ft), Dombivli flat ₹71,000/sq m (₹6,596/sq ft); site says figures come from official documents but advises verifying with the sub-registrar. Official IGR e-ASR not opened |

Sources tried and not usable: CPWD Plinth Area Rates 2025 (official PDF not found online; only the preface
was readable), IGR Maharashtra e-ASR (portal requires interactive selection), 99acres and Magicbricks
locality pages (refuse automated access), listed-developer annual reports for marketing cost (not retrieved),
Business Standard 2020 article on developer loan rates (subscription required).

## 3. Input-by-input check

Values are the base case in `feasibility/inputs.py`. "Fit" says where the value sits in the published range.

| Input | Base case | What the sources say | Fit |
|---|---|---|---|
| Saleable area | 1,00,000 sq ft | A design choice. Roughly one 1-acre plot at FSI 2.5 in a KDMC or CIDCO area, or two 15-storey wings of 2 BHK units. | Assumption |
| Selling price | ₹7,500 / sq ft | S1: Mumbai average ₹95,326/sq m = ₹8,856/sq ft in H2 2025, +7% YoY. S2: Panvel average ₹7,835 (range ₹5,830 to 9,839); Dombivli East transaction benchmark ₹8,500 and asking ₹9,700; Kalyan *registered* rate ₹7,900 over 859 deals. S19: ready reckoner Kalyan ₹6,039 and Dombivli ₹6,596 per sq ft. | Within the registered-price range for Panvel, Kalyan and Dombivli; 15% below the Mumbai average; about 15% to 25% above the ready reckoner, which is normal |
| Construction cost | ₹3,000 / sq ft | S4: Mumbai standard quality ₹3,086 as of Oct 2026 (basic ₹2,407, premium ₹4,166), excluding professional fees. Other calculator sites give ₹2,800 to 4,500 for a 7-floor structure. S3: JLL 2026 gives ₹3,900 to 4,900 for *commercial* high-rise in Mumbai; no residential figure. | Low-to-mid of the range for a mid-segment tower. A fully loaded figure with external development, contingency and consultants would be ₹3,500 to 4,000. The +20% sensitivity step covers this |
| Land cost | ₹20 cr | S5: JLL puts the transacted MMR land cost at about ₹17 cr per acre in 2024, up from ₹11 cr in 2022. S6: Panvel asking prices ₹3.2 cr per acre (Karnala) to ₹12 cr per acre (Somtane). | Consistent with one acre at the MMR average plus stamp duty and transfer costs. Generous for outer Panvel, tight for Kalyan town centre |
| Land payment month | 1 | Assumption: outright purchase. Joint development or deferred payment would change the equity profile. | Assumption |
| Approval and statutory costs | ₹3 cr (10% of construction cost, 5.3% of total cost) | S7: for redevelopment inside Greater Mumbai, direct BMC charges were 23% to 32% of project cost (average 27%) at 2017 rates, excluding premium FSI and TDR. S8: fungible FSI (up to 35% for residential) carries a premium of 60% of the ready reckoner rate. Outside BMC limits (KDMC, CIDCO, Panvel) premiums are far lower but no published share was found. | Low for Greater Mumbai; plausible for the periphery. This is the weakest input. The −20% to +20% sensitivity step is too narrow to reach BMC levels, so a Greater Mumbai case must be entered explicitly |
| Approval window | months 1 to 3 | No published benchmark found. In practice Mumbai approvals take 6 to 12 months; the model spreads the *spend* over 3 months and starts construction in month 4. | Optimistic on time; the "sales launch delay" and "construction delay" drivers show the cost of slippage |
| Construction window | months 4 to 30 (27 months) | S18: a 24-tower Bengaluru job of 18 to 29 storeys was let on a 42-month schedule (2014); a 41-storey Parel tower is listed at 36 months. A single mid-rise project is shorter. | Plausible for one or two mid-rise wings; aggressive for a tall tower |
| Sales window | months 7 to 30 | S1: Mumbai quarters-to-sell was 6.4 quarters (19 months) city-wide and 3.9 quarters for the ₹20 to 50 mn segment in H2 2025. | Consistent: 24-month sell-out for a mid-segment project is in line with city absorption |
| Booking share | 20% at booking | S15: RERA s.13(1) caps the advance before a registered agreement at 10%. S16: two MahaRERA-format schedules take 10% at booking, 20% on agreement, 15% at plinth, 5% per slab (or 25% across slabs) and the last 30% at finishing stages. | Equivalent to 10% booking plus 10% on agreement in the same month |
| Instalments | 6 equal monthly instalments | S16: real construction-linked plans spread the balance over slab milestones, typically 18 to 30 months, not 6. | **Optimistic.** The model collects cash faster than a construction-linked plan would. See section 4 |
| Marketing cost | 2% of collections | S7: marketing was 3% to 4% of *project cost* in the MCHI examples (₹2,500 per sq ft of carpet at a ₹50,000 sale rate, 5%). S17: developer channel-partner commission is 2% to 5% of base price plus 18% GST; a 2018 report had brokers demanding 3% to 5%. | Low. 3% to 4% of revenue is a better central figure where channel partners are used. The custom scenario sliders do not cover marketing; change the input directly |
| Debt share | 50% of land, approvals and construction | S7: finance cost was 11% of project cost in both MCHI examples, which at 12% to 14% rates over 3 years implies roughly half the cost base funded by debt. S15: RERA's 70% escrow rule limits how customer collections can be used, which is why lenders fund the early spend. | Consistent |
| Interest rate | 12% p.a. | S9: policy repo rate 5.50% from 7 October 2026 (raised 25 bp, stance "calibrated tightening"). S10: nationalised banks 10% to 12%, private banks 11% to 13%, NBFC category A 11% to 14%, category B 13% to 17%. | Mid-range for a bank or category-A NBFC. The +2 pp sensitivity step reaches the NBFC category-B floor |
| Repayment sweep | 50% of collections | Assumption. Lender term sheets commonly sweep 50% to 100% of receivables into an escrow for repayment. No published MMR figure found. | Assumption |
| Tax rate | 25% | S12: s.115BAA gives 22% + 10% surcharge + 4% cess = 25.168%. | 0.17 pp low; immaterial. Team may change to 25.17% |
| Discount rate | 15% p.a. | S13: EY/NSE 2024 survey, cost of equity for real estate 16.4%, overall India 14.2%, risk-free rate plus market risk premium. S14: developer survey (Australia and New Zealand, 225 respondents): median IRR hurdle 18% (SD 4.85%), median margin on development cost 20%. | Slightly below the real estate cost of equity. A 16.4% rate is defensible; the +1 and +2 pp sensitivity rows show the effect (NPV stays positive) |
| Horizon | 36 months minimum | Follows from the windows above; the tool extends it automatically. | Derived |

## 4. What the checks mean for the base case

- **Three inputs lean optimistic:** the 6-month instalment pattern, the 2% marketing cost, and the approval cost if the site is inside Greater Mumbai. Each one taken alone keeps the base case viable (see the sensitivity table), but a user appraising a real MMR site should start from a construction-linked payment schedule, 3% to 4% marketing, and the actual MCGM premium estimate.
- **Two inputs are near the published central value:** selling price for Panvel or upper Dombivli, and the interest rate.
- **Discount rate:** 15% is below the 16.4% cost of equity the EY/NSE survey reports for Indian real estate. The team kept 15% because it is the commonly taught hurdle and the sensitivity row shows the result at 16% and 17%.
- **No input was changed after this check.** Changing the base case would have invalidated the Excel benchmark, the validation report and the screenshots. The decision, and the reasoning, is recorded in the AI usage log (entry 28).

## 5. Method note

The appraisal method is a monthly discounted cash flow at the equity level, with the project (unlevered)
IRR shown alongside. Equity NPV at the discount rate, equity IRR, payback, profit on cost and break-even
price are computed exactly as described in section 10 of the user manual; the formulas are reproduced
without change in the benchmark workbook so that the Validation Engineer can check them by hand. Sensitivity
is one-at-a-time; scenarios are three fixed combinations plus a custom slider set. No probability
distributions are used.

## 6. How to re-verify a source

1. **Ready reckoner (official):** open igrmaharashtra.gov.in, choose e-ASR, select Thane district, Kalyan taluka,
   the village, and read the residential flat rate per sq m. Multiply by 0.0929 for ₹ per sq ft. Do the same for
   Raigad district, Panvel taluka.
2. **Knight Frank:** the H2 2025 PDF is 80 pages; the Mumbai residential text and micro-market charts are on PDF pages 55 and 56.
3. **RBI:** press release ID 63742 on rbi.org.in is the MPC resolution of 7 October 2026 (opened and confirmed).
4. **EY/NSE survey:** Chart 5, "Industry-wise discount rates", printed page 14 (PDF page 15).
5. **MCHI paper:** the "Project cost break up Khar" and "Andheri" tables and the "Inferences" page.

Every source in the table was opened on 5 November 2026, S14 by a team member in a browser and the rest by
the AI's fetch tools. S11 was withdrawn (paywalled). If any figure is later found to differ from what is
written here, correct this file and note the correction in the AI usage log.
