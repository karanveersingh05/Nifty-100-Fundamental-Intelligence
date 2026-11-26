(() => {
  
  const menuBtn = document.querySelector(".menu-toggle");
  const mainNav = document.querySelector("#main-nav");

  if (menuBtn && mainNav) {
    menuBtn.addEventListener("click", () => {
      const open = menuBtn.getAttribute("aria-expanded") !== "true";
      menuBtn.setAttribute("aria-expanded", String(open));
      mainNav.classList.toggle("is-open", open);
    });

    mainNav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        menuBtn.setAttribute("aria-expanded", "false");
        mainNav.classList.remove("is-open");
      });
    });
  }

  
  const stocksData = {
    "TCS": {
      symbol: "TCS",
      name: "Tata Consultancy Services Ltd",
      sector: "IT",
      overall_score: 57.92,
      health_label: "AVERAGE",
      profitability_score: 44.27,
      growth_score: 12.0,
      leverage_score: 100.0,
      cashflow_score: 100.0,
      trend_score: 59.02,
      sales_cr: 240893,
      net_profit_cr: 46099,
      npm_pct: 19.1,
      opm_pct: 27.0,
      debt_to_equity: 0.09,
      free_cash_flow_cr: 50429,
      cash_conversion_ratio: 0.96,
      roe_pct: 3.0,
      sales_cagr_3y: 3.0,
      pros: [
        "Global Tier-1 technology partner with deep enterprise multi-year digital transformation contracts.",
        "Conservative capital structure with low Debt-to-Equity ratio of 0.09.",
        "Exceptional net profit margin of 19.4%, exhibiting pricing power over input costs.",
        "Positive free cash flow generation strengthening internal liquidity and expansion reserves."
      ],
      cons: [
        "Zero or negligible dividend payout over recent reporting periods.",
        "Subdued 3-year Return on Equity trailing top industry benchmarks.",
        "Sluggish 3-year sales growth (3.0% CAGR) indicating near-term market saturation."
      ]
    },
    "RELIANCE": {
      symbol: "RELIANCE",
      name: "Reliance Industries Ltd",
      sector: "Conglomerate",
      overall_score: 56.09,
      health_label: "AVERAGE",
      profitability_score: 50.0,
      growth_score: 0.0,
      leverage_score: 100.0,
      cashflow_score: 100.0,
      trend_score: 57.29,
      sales_cr: 899041,
      net_profit_cr: 79020,
      npm_pct: 8.8,
      opm_pct: 18.0,
      debt_to_equity: 0.58,
      free_cash_flow_cr: 45207,
      cash_conversion_ratio: 2.01,
      roe_pct: 10.0,
      sales_cagr_3y: 0.0,
      pros: [
        "Established market positioning with robust operational brand heritage across energy, telecom, and retail.",
        "Manageable debt obligations with Debt-to-Equity maintained at 0.58.",
        "Healthy net profit margin sustaining consistent bottom-line returns.",
        "Positive free cash flow generation strengthening internal liquidity and expansion reserves."
      ],
      cons: [
        "Heavy ongoing capex cycle requires sustained debt management and timely project execution.",
        "Valuation metrics reflect premium multiples given the company's established market leadership."
      ]
    },
    "HDFCBANK": {
      symbol: "HDFCBANK",
      name: "HDFC Bank Ltd",
      sector: "Banking",
      overall_score: 45.45,
      health_label: "AVERAGE",
      profitability_score: 52.15,
      growth_score: 12.0,
      leverage_score: 30.0,
      cashflow_score: 75.0,
      trend_score: 81.11,
      sales_cr: 283649,
      net_profit_cr: 65446,
      npm_pct: 23.1,
      opm_pct: 32.0,
      debt_to_equity: 6.81,
      free_cash_flow_cr: 35669,
      cash_conversion_ratio: 0.29,
      roe_pct: 3.0,
      sales_cagr_3y: 3.0,
      pros: [
        "Strong low-cost CASA deposit franchise backed by extensive nationwide branch network.",
        "Strong capital adequacy ratio and well-diversified loan/asset book across retail and corporate sectors.",
        "Exceptional net profit margin exhibiting pricing power over financing costs.",
        "Positive free cash flow generation strengthening internal liquidity."
      ],
      cons: [
        "Exposed to cyclical asset-quality deterioration and net interest margin (NIM) compression.",
        "Elevated financial leverage typical of lending institutions requires strict capital buffering.",
        "Subdued 3-year Return on Equity trailing historical pre-merger averages."
      ]
    },
    "TATAMOTORS": {
      symbol: "TATAMOTORS",
      name: "Tata Motors Ltd",
      sector: "Auto",
      overall_score: 57.50,
      health_label: "AVERAGE",
      profitability_score: 50.0,
      growth_score: 0.0,
      leverage_score: 75.0,
      cashflow_score: 100.0,
      trend_score: 100.0,
      sales_cr: 437928,
      net_profit_cr: 31807,
      npm_pct: 7.3,
      opm_pct: 14.0,
      debt_to_equity: 1.26,
      free_cash_flow_cr: 45133,
      cash_conversion_ratio: 2.14,
      roe_pct: 35.0,
      sales_cagr_3y: 0.0,
      pros: [
        "Dominant leadership in Indian electric passenger vehicles and commercial fleet segments.",
        "Robust multi-year turnaround at Jaguar Land Rover (JLR) driving sharp debt reduction.",
        "Strong operating cash flow conversion comfortably exceeding net profit.",
        "Substantial improvement in ROE from operational cost discipline."
      ],
      cons: [
        "Vulnerable to global automotive demand cycles and supply chain pressures.",
        "Moderate financial leverage with ongoing debt retirement milestones."
      ]
    },
    "ITC": {
      symbol: "ITC",
      name: "ITC Ltd",
      sector: "Consumer Goods",
      overall_score: 56.76,
      health_label: "AVERAGE",
      profitability_score: 50.0,
      growth_score: 0.0,
      leverage_score: 100.0,
      cashflow_score: 100.0,
      trend_score: 61.76,
      sales_cr: 70866,
      net_profit_cr: 20751,
      npm_pct: 29.3,
      opm_pct: 37.0,
      debt_to_equity: 0.00,
      free_cash_flow_cr: 18742,
      cash_conversion_ratio: 0.83,
      roe_pct: 28.5,
      sales_cagr_3y: 0.0,
      pros: [
        "Virtually debt-free balance sheet with pristine liquidity reserves.",
        "Industry-leading net profit margin of 29.3% backed by an irreplaceable pan-India distribution network.",
        "Consistent high dividend payout track record rewarding long-term shareholders.",
        "Growing non-cigarette FMCG brand portfolio providing structural compounding."
      ],
      cons: [
        "Regulatory and taxation sensitivity around core tobacco operations.",
        "Valuation multiple reflects mature consumer enterprise characteristics."
      ]
    },
    "MARUTI": {
      symbol: "MARUTI",
      name: "Maruti Suzuki India Ltd",
      sector: "Auto",
      overall_score: 62.50,
      health_label: "GOOD",
      profitability_score: 50.0,
      growth_score: 0.0,
      leverage_score: 100.0,
      cashflow_score: 100.0,
      trend_score: 100.0,
      sales_cr: 141858,
      net_profit_cr: 13488,
      npm_pct: 9.5,
      opm_pct: 13.0,
      debt_to_equity: 0.00,
      free_cash_flow_cr: 4936,
      cash_conversion_ratio: 1.25,
      roe_pct: 15.8,
      sales_cagr_3y: 0.0,
      pros: [
        "Uncontested passenger vehicle market leadership with unmatched service footprint across India.",
        "Zero long-term borrowings resulting in a debt-free capital structure.",
        "High cash conversion ratio (1.25x) confirming earnings quality.",
        "Strong recent volume momentum in higher-margin SUV portfolio."
      ],
      cons: [
        "Elevated competitive intensity in compact SUV and premium vehicle segments.",
        "Moderate transition pace toward pure battery electric vehicle lineups."
      ]
    },
    "DMART": {
      symbol: "DMART",
      name: "Avenue Supermarts Ltd",
      sector: "Retail",
      overall_score: 57.81,
      health_label: "AVERAGE",
      profitability_score: 50.0,
      growth_score: 0.0,
      leverage_score: 100.0,
      cashflow_score: 100.0,
      trend_score: 68.75,
      sales_cr: 50789,
      net_profit_cr: 2536,
      npm_pct: 5.0,
      opm_pct: 8.0,
      debt_to_equity: 0.03,
      free_cash_flow_cr: 278,
      cash_conversion_ratio: 1.08,
      roe_pct: 14.5,
      sales_cagr_3y: 0.0,
      pros: [
        "Unique store-ownership model resulting in the lowest cost-of-retailing in India.",
        "Virtually debt-free balance sheet enabling self-funded real estate acquisitions.",
        "High inventory turnover and superior bargaining leverage with FMCG vendors.",
        "Consistent operating cash flow generation exceeding reported profits."
      ],
      cons: [
        "Thin retail margin structure with net margins hovering near 5%.",
        "Stock trades at premium valuation multiples pricing in aggressive multi-year store rollouts."
      ]
    },
    "ADANIGREEN": {
      symbol: "ADANIGREEN",
      name: "Adani Green Energy Ltd",
      sector: "Energy",
      overall_score: 43.08,
      health_label: "AVERAGE",
      profitability_score: 50.0,
      growth_score: 0.0,
      leverage_score: 30.0,
      cashflow_score: 75.0,
      trend_score: 65.57,
      sales_cr: 9220,
      net_profit_cr: 1260,
      npm_pct: 13.7,
      opm_pct: 79.0,
      debt_to_equity: 6.60,
      free_cash_flow_cr: -13347,
      cash_conversion_ratio: 6.12,
      roe_pct: 18.0,
      sales_cagr_3y: 0.0,
      pros: [
        "Strategic renewable utility assets with long-term 25-year Power Purchase Agreements (PPAs).",
        "Exceptional operating profit margin (79%) reflecting low marginal cost of solar and wind generation.",
        "Strong government policy tailwind prioritizing domestic clean energy transition."
      ],
      cons: [
        "High debt burden with Debt-to-Equity of 6.60 resulting in substantial interest expense drag.",
        "Negative free cash flow due to massive ongoing capital expenditures for gigawatt capacity additions.",
        "Modest interest coverage buffer creates sensitivity to sovereign and international borrowing rates."
      ]
    },
    "SUNPHARMA": {
      symbol: "SUNPHARMA",
      name: "Sun Pharmaceuticals Industries Ltd",
      sector: "Healthcare",
      overall_score: 59.42,
      health_label: "AVERAGE",
      profitability_score: 50.0,
      growth_score: 0.0,
      leverage_score: 100.0,
      cashflow_score: 100.0,
      trend_score: 79.48,
      sales_cr: 48497,
      net_profit_cr: 10137,
      npm_pct: 20.9,
      opm_pct: 27.0,
      debt_to_equity: 0.05,
      free_cash_flow_cr: 8940,
      cash_conversion_ratio: 1.15,
      roe_pct: 16.5,
      sales_cagr_3y: 0.0,
      pros: [
        "Market leader in Indian domestic formulations with top prescription market share across therapies.",
        "Strong global specialty dermatology and ophthalmology innovative pipeline.",
        "Conservative capital structure with negligible debt and high free cash flow generation.",
        "Exceptional net profit margin of 20.9% providing resilience against regulatory price caps."
      ],
      cons: [
        "Regulatory compliance scrutiny from the US FDA across manufacturing facilities.",
        "Price erosion in legacy US generic commodity markets."
      ]
    },
    "COALINDIA": {
      symbol: "COALINDIA",
      name: "Coal India Ltd",
      sector: "Energy",
      overall_score: 61.80,
      health_label: "GOOD",
      profitability_score: 50.0,
      growth_score: 0.0,
      leverage_score: 100.0,
      cashflow_score: 100.0,
      trend_score: 95.36,
      sales_cr: 142340,
      net_profit_cr: 37402,
      npm_pct: 26.3,
      opm_pct: 35.0,
      debt_to_equity: 0.08,
      free_cash_flow_cr: 28410,
      cash_conversion_ratio: 1.05,
      roe_pct: 42.0,
      sales_cagr_3y: 0.0,
      pros: [
        "Monopolistic commercial coal mining rights in India meeting critical baseload thermal power demand.",
        "Very low Debt-to-Equity ratio of 0.08 paired with massive cash balances.",
        "Superior Return on Equity (ROE exceeding 40%) delivering exceptional capital efficiency.",
        "Consistently generous dividend yields among the highest on the Nifty index."
      ],
      cons: [
        "Long-term structural decarbonization and transition risks toward renewable power.",
        "Regulated pricing ceilings limit full market-price monetization of coal assets."
      ]
    }
  };

  
  let currentStock = "TCS";
  let currentTab = "scorecard";

  
  const buttons = document.querySelectorAll(".stock-btn");
  const stockName = document.querySelector("#stock-name");
  const stockSymbol = document.querySelector("#stock-symbol");
  const stockSector = document.querySelector("#stock-sector");
  const stockScore = document.querySelector("#stock-score");
  const stockBadge = document.querySelector("#stock-badge");

  const scoreProf = document.querySelector("#score-prof");
  const scoreGrow = document.querySelector("#score-grow");
  const scoreLev = document.querySelector("#score-lev");
  const scoreCash = document.querySelector("#score-cash");
  const scoreTrend = document.querySelector("#score-trend");

  const metricSales = document.querySelector("#metric-sales");
  const metricProfit = document.querySelector("#metric-profit");
  const metricNpm = document.querySelector("#metric-npm");
  const metricDte = document.querySelector("#metric-dte");

  const prosList = document.querySelector("#pros-list");
  const consList = document.querySelector("#cons-list");
  const jsonPreview = document.querySelector("#json-preview");

  function renderStock(symbol) {
    const data = stocksData[symbol];
    if (!data) return;

    currentStock = symbol;

    
    buttons.forEach((btn) => {
      btn.classList.toggle("is-active", btn.dataset.symbol === symbol);
    });

    
    stockName.textContent = data.name;
    stockSymbol.textContent = `(${data.symbol})`;
    stockSector.textContent = data.sector;
    stockScore.textContent = data.overall_score.toFixed(1);

    
    stockBadge.textContent = data.health_label;
    stockBadge.className = `label-badge label-${data.health_label.toLowerCase()}`;

    
    scoreProf.textContent = data.profitability_score.toFixed(1);
    scoreGrow.textContent = data.growth_score.toFixed(1);
    scoreLev.textContent = data.leverage_score.toFixed(1);
    scoreCash.textContent = data.cashflow_score.toFixed(1);
    scoreTrend.textContent = data.trend_score.toFixed(1);

    
    metricSales.textContent = `₹${data.sales_cr.toLocaleString()} Cr`;
    metricProfit.textContent = `₹${data.net_profit_cr.toLocaleString()} Cr`;
    metricNpm.textContent = `${data.npm_pct}%`;
    metricDte.textContent = data.debt_to_equity.toFixed(2);

    
    prosList.innerHTML = "";
    data.pros.forEach((proText) => {
      const li = document.createElement("li");
      li.className = "pro-li";
      li.innerHTML = `<span class="bullet">✓</span> <span>${proText}</span>`;
      prosList.appendChild(li);
    });

    
    consList.innerHTML = "";
    data.cons.forEach((conText) => {
      const li = document.createElement("li");
      li.className = "con-li";
      li.innerHTML = `<span class="bullet">✕</span> <span>${conText}</span>`;
      consList.appendChild(li);
    });

    
    const apiPayload = {
      status: "success",
      ticker: data.symbol,
      company: data.name,
      sector: data.sector,
      health_score: data.overall_score,
      health_label: data.health_label,
      score_breakdown: {
        profitability: data.profitability_score,
        growth: data.growth_score,
        solvency: data.leverage_score,
        cash_flow: data.cashflow_score,
        momentum: data.trend_score
      },
      warehouse_metrics: {
        revenue_cr: data.sales_cr,
        net_profit_cr: data.net_profit_cr,
        net_profit_margin_pct: data.npm_pct,
        debt_to_equity: data.debt_to_equity,
        free_cash_flow_cr: data.free_cash_flow_cr
      },
      audited_insights: {
        pros_count: data.pros.length,
        cons_count: data.cons.length
      }
    };
    jsonPreview.textContent = JSON.stringify(apiPayload, null, 2);
  }

  
  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      renderStock(btn.dataset.symbol);
    });
  });

  
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");

  tabButtons.forEach((tab) => {
    tab.addEventListener("click", () => {
      const target = tab.dataset.tab;
      currentTab = target;

      tabButtons.forEach((b) => b.classList.toggle("is-active", b === tab));
      tabPanes.forEach((p) => p.classList.toggle("is-active", p.id === `pane-${target}`));
    });
  });

  
  const quickSearch = document.querySelector("#stock-quick-search");
  if (quickSearch) {
    quickSearch.addEventListener("input", (e) => {
      const val = e.target.value.toUpperCase();
      buttons.forEach((btn) => {
        const sym = btn.dataset.symbol.toUpperCase();
        btn.style.display = sym.includes(val) ? "inline-block" : "none";
      });
    });
  }

  
  renderStock("TCS");
})();
