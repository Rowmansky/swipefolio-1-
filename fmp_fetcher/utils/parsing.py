# fmp_fetcher/utils/parsing.py
# Contains helper functions for safe type conversion and
# functions to parse FMP API responses into formats suitable for Supabase tables (v3.1 Schema).

import logging
from typing import List, Dict, Any, Optional
from decimal import Decimal, InvalidOperation
from datetime import date, datetime

logger = logging.getLogger(__name__) # Use module-specific logger

# --- Generic Helper Functions ---

def safe_decimal(value: Any, default: Optional[Decimal] = None) -> Optional[Decimal]:
    """Safely convert a value to Decimal, handling None, empty strings, and errors."""
    if value is None or value == '':
        return default
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        # Log only if value wasn't already default=None, to avoid noise
        if default is None or value != default:
             logger.debug(f"Could not convert '{value}' (type: {type(value)}) to Decimal. Returning default: {default}")
        return default

def safe_int(value: Any, default: Optional[int] = None) -> Optional[int]:
    """Safely convert a value to int, handling None, empty strings, floats, and errors."""
    if value is None or value == '':
        return default
    try:
        # Handle potential float strings like '123.0' or actual floats
        return int(Decimal(str(value)))
    except (ValueError, TypeError, InvalidOperation):
         if default is None or value != default:
            logger.debug(f"Could not convert '{value}' (type: {type(value)}) to int. Returning default: {default}")
         return default

def safe_bool(value: Any, default: Optional[bool] = None) -> Optional[bool]:
    """Safely convert a value to bool, handling None."""
    if value is None:
        return default
    # Handles True, False, 'true', 'false', 'True', 'False', 1, 0 reasonably
    if isinstance(value, str):
        return value.lower() in ['true', '1', 't', 'y', 'yes']
    try:
        return bool(value)
    except Exception:
        if default is None or value != default:
            logger.debug(f"Could not convert '{value}' (type: {type(value)}) to bool. Returning default: {default}")
        return default

def safe_text(value: Any, default: Optional[str] = None) -> Optional[str]:
    """Safely convert a value to text, handling None."""
    if value is None:
        return default
    try:
        return str(value)
    except Exception:
         if default is None or value != default:
            logger.debug(f"Could not convert '{value}' (type: {type(value)}) to string. Returning default: {default}")
         return default

# --- Table-Specific Parsing Functions (v3.1 Schema) ---

# 1. Stocks Table
def parse_stock_profile(api_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Parses FMP Company Profile API data (/profile/{symbol}) into the 'stocks' table format."""
    if not api_data or not api_data.get('symbol'):
        logger.warning("Received empty or invalid profile data from API.")
        return None
    profile = {
        'symbol': api_data.get('symbol'),
        'company_name': api_data.get('companyName'),
        'cik': api_data.get('cik'),
        'exchange': api_data.get('exchange'),
        'exchange_short_name': api_data.get('exchangeShortName'),
        'industry': api_data.get('industry'),
        'sector': api_data.get('sector'),
        'description': api_data.get('description'),
        'website': api_data.get('website'),
        'ceo': api_data.get('ceo'),
        'employees': safe_int(api_data.get('fullTimeEmployees')),
        'country': api_data.get('country'),
        'hq_address': api_data.get('address'), # Assuming FMP 'address' field is HQ
        'beta': safe_decimal(api_data.get('beta')),
        'ipo_date': api_data.get('ipoDate'),
        'market_cap': safe_int(api_data.get('mktCap')),
        'is_actively_trading': safe_bool(api_data.get('isActivelyTrading')),
        'is_etf': safe_bool(api_data.get('isEtf')),
        'is_fund': safe_bool(api_data.get('isFund'))
    }
    return profile

def parse_bulk_profiles(api_data_list: List[Dict[str, Any]], target_symbols: List[str]) -> List[Dict[str, Any]]:
    """Parses a list of FMP Company Profiles (from bulk API) for target symbols."""
    parsed_profiles = []
    target_set = set(target_symbols)
    for item in api_data_list:
        if item.get('symbol') in target_set:
             parsed = parse_stock_profile(item)
             if parsed:
                 parsed_profiles.append(parsed)
    logger.info(f"Parsed {len(parsed_profiles)} profiles for {len(target_set)} target symbols from bulk data.")
    return parsed_profiles

# 2. Daily Stock Prices
def parse_daily_price(api_data: Dict[str, Any], symbol_override: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Parses FMP EOD data point into 'stock_prices_daily' format."""
    # Use symbol_override if provided (e.g., from bulk EOD which might not have symbol in each item)
    symbol = symbol_override if symbol_override else api_data.get('symbol')
    if not api_data or not symbol or not api_data.get('date'):
        logger.warning(f"Received incomplete daily price data: {api_data}")
        return None
    price_record = {
        'symbol': symbol,
        'date': api_data.get('date'),
        'open': safe_decimal(api_data.get('open')),
        'high': safe_decimal(api_data.get('high')),
        'low': safe_decimal(api_data.get('low')),
        'close': safe_decimal(api_data.get('close')),
        'adj_close': safe_decimal(api_data.get('adjClose')),
        'volume': safe_int(api_data.get('volume')),
        'unadjusted_volume': safe_int(api_data.get('unadjustedVolume')),
        'change': safe_decimal(api_data.get('change')),
        'change_percent': safe_decimal(api_data.get('changePercent')),
        'vwap': safe_decimal(api_data.get('vwap')),
        'label': api_data.get('label'),
        'change_over_time': safe_decimal(api_data.get('changeOverTime'))
    }
    return price_record

def parse_bulk_daily_prices(api_data_list: List[Dict[str, Any]], target_symbols: List[str], date_override: Optional[str] = None) -> List[Dict[str, Any]]:
    """Parses a list of EOD data (from bulk API /eod-bulk) for target symbols."""
    parsed_prices = []
    target_set = set(target_symbols)
    for item in api_data_list:
        # Bulk EOD might not include symbol in each item, rely on filtering later or assume structure
        # Let's assume 'symbol' is present based on FMP docs usually listing it
        symbol = item.get('symbol')
        if symbol and symbol in target_set:
             # Use date_override if bulk API doesn't include date per item
             if date_override and 'date' not in item:
                 item['date'] = date_override
             parsed = parse_daily_price(item, symbol_override=symbol) # Pass symbol explicitly
             if parsed:
                 parsed_prices.append(parsed)
    logger.info(f"Parsed {len(parsed_prices)} daily price records for {len(target_set)} target symbols from bulk data.")
    return parsed_prices

# 3. Financial Statements
def parse_financial_statement(api_data: Dict[str, Any], symbol: str, statement_type: str) -> Optional[Dict[str, Any]]:
    """Parses FMP Financial Statement data (income, balance, cashflow) into 'financial_statements' format."""
    if not api_data or not api_data.get('date') or not api_data.get('period'):
        logger.warning(f"Received incomplete financial statement data for {symbol}, type {statement_type}: {api_data}")
        return None
    period_val = safe_text(api_data.get('period', '')).lower()
    if period_val not in ['annual', 'quarter']:
         logger.warning(f"Invalid period value '{period_val}' found for {symbol} statement. Skipping record.")
         return None

    statement_record = {
        'symbol': symbol,
        'report_date': api_data.get('date'),
        'filing_date': api_data.get('fillingDate'), # Note FMP potential typo 'fillingDate'
        'accepted_date': api_data.get('acceptedDate'),
        'calendar_year': safe_int(api_data.get('calendarYear')),
        'period': period_val,
        'statement_type': statement_type.lower(),
        'cik': api_data.get('cik'),
        'link': api_data.get('link'),
        'source_filing_url': api_data.get('finalLink'),
        'data': api_data # Store the original JSON data
    }
    return statement_record

def parse_bulk_financial_statements(api_data_list: List[Dict[str, Any]], statement_type: str, target_symbols: List[str]) -> List[Dict[str, Any]]:
    """Parses a list of Financial Statements (from bulk API) into table format."""
    parsed_statements = []
    target_set = set(target_symbols)
    for item in api_data_list:
        symbol = item.get('symbol')
        if symbol and symbol in target_set:
            parsed = parse_financial_statement(item, symbol, statement_type)
            if parsed:
                parsed_statements.append(parsed)
    logger.info(f"Parsed {len(parsed_statements)} {statement_type} statements for {len(target_set)} target symbols from bulk data.")
    return parsed_statements

# 4. Key Metrics TTM
def parse_key_metrics_ttm(api_data: Dict[str, Any], symbol: Optional[str] = None, ratios_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Parses combined FMP TTM Key Metrics & Ratios API data into 'key_metrics_ttm' format.
       Handles individual symbol responses or items from a bulk list.
       
       Args:
           api_data: The key metrics API data
           symbol: Optional symbol (if not included in api_data)
           ratios_data: Optional ratios API data to merge with key metrics for complete metrics
    """
    if not api_data:
        logger.warning(f"Received empty TTM key metrics data.")
        return None
    
    # Extract symbol from data if not provided as argument
    symbol = symbol or api_data.get('symbol')
    
    if not symbol:
        logger.warning(f"No symbol found in TTM key metrics data.")
        return None

    # Log the available fields for debugging
    if logging.getLogger().isEnabledFor(logging.DEBUG):
        logger.debug(f"TTM metrics for {symbol} has these fields: {', '.join(api_data.keys())}")
        if ratios_data:
            logger.debug(f"TTM ratios for {symbol} has these fields: {', '.join(ratios_data.keys())}")

    # Combine data from both sources if ratios data is provided
    combined_data = api_data.copy()
    if ratios_data:
        # For any fields in ratios_data that aren't in api_data, add them to combined_data
        for key, value in ratios_data.items():
            if key not in combined_data or combined_data[key] is None or combined_data[key] == "":
                combined_data[key] = value
                
        logger.info(f"Combined data from both metrics and ratios endpoints for {symbol}")

    # Helper function to get field with alternative field names
    def get_field_with_alternatives(primary_key, alt_keys=None):
        alt_keys = alt_keys or []
        value = combined_data.get(primary_key)
        if value is None or value == "":
            for alt_key in alt_keys:
                alt_value = combined_data.get(alt_key)
                if alt_value is not None and alt_value != "":
                    logger.info(f"Using alternative key '{alt_key}' instead of '{primary_key}' for {symbol}")
                    return alt_value
        return value

    # Fix date_calculated - very important for historical records
    date_calculated = combined_data.get('date')
    if not date_calculated:
        # Try various date fields that might be present
        date_alternatives = ['date', 'period', 'calendarDate', 'fillingDate', 'reportDate', 'acceptedDate', 'formFiled']
        for date_field in date_alternatives:
            if combined_data.get(date_field):
                date_calculated = combined_data.get(date_field)
                logger.info(f"Using {date_field} for date_calculated: {date_calculated}")
                break
                
    # If still no date, use today's date as fallback for TTM metrics
    if not date_calculated:
        from datetime import date
        date_calculated = date.today().isoformat()
        logger.debug(f"Using today's date for TTM metrics for {symbol}: {date_calculated}")

    # Map API fields to database columns using safe conversions
    # This list needs to be comprehensive based on the v3.1 key_metrics_ttm table schema
    ttm_metrics = {
        'symbol': symbol,
        'date_calculated': date_calculated,

        # Per Share Metrics TTM
        'revenue_per_share_ttm': safe_decimal(get_field_with_alternatives('revenuePerShareTTM', ['revenuePerShare'])),
        'net_income_per_share_ttm': safe_decimal(get_field_with_alternatives('netIncomePerShareTTM', ['netIncomePerShare'])),
        'operating_cash_flow_per_share_ttm': safe_decimal(get_field_with_alternatives('operatingCashFlowPerShareTTM', ['operatingCashFlowPerShare'])),
        'free_cash_flow_per_share_ttm': safe_decimal(get_field_with_alternatives('freeCashFlowPerShareTTM', ['freeCashFlowPerShare'])),
        'cash_per_share_ttm': safe_decimal(get_field_with_alternatives('cashPerShareTTM', ['cashPerShare'])),
        'book_value_per_share_ttm': safe_decimal(get_field_with_alternatives('bookValuePerShareTTM', ['bookValuePerShare'])),
        'tangible_book_value_per_share_ttm': safe_decimal(get_field_with_alternatives('tangibleBookValuePerShareTTM', ['tangibleBookValuePerShare'])),
        'shareholders_equity_per_share_ttm': safe_decimal(get_field_with_alternatives('shareholdersEquityPerShareTTM', ['shareholdersEquityPerShare'])),
        'interest_debt_per_share_ttm': safe_decimal(get_field_with_alternatives('interestDebtPerShareTTM', ['interestDebtPerShare'])),
        'capex_per_share_ttm': safe_decimal(get_field_with_alternatives('capexPerShareTTM', ['capexPerShare'])),

        # Market Valuation & Enterprise Value TTM - from key-metrics-ttm endpoint
        'market_cap_ttm': safe_int(get_field_with_alternatives('marketCapTTM', ['marketCap', 'mktCap'])),
        'enterprise_value_ttm': safe_int(get_field_with_alternatives('enterpriseValueTTM', ['enterpriseValue', 'ev'])),
        
        # Price ratios - often in ratios-ttm endpoint
        'pe_ratio_ttm': safe_decimal(get_field_with_alternatives('peRatioTTM', [
            'peRatio', 'priceEarningsRatio', 'priceEarningsRatioTTM', 'priceToEarnings', 'p/e', 'price/earnings', 'priceToEarningsRatioTTM'
        ])),
        
        'price_to_sales_ratio_ttm': safe_decimal(get_field_with_alternatives('priceToSalesRatioTTM', [
            'priceToSalesRatio', 'pSRatio', 'priceToSales', 'p/s', 'price/sales'
        ])),
        
        'pocfratio_ttm': safe_decimal(get_field_with_alternatives('pocfratioTTM', [
            'pocfratio', 'priceToOperatingCashFlowRatio', 'priceOperatingCashFlowRatio', 'priceToOCF', 'priceToOperatingCashFlowRatioTTM'
        ])),
        
        'pfcf_ratio_ttm': safe_decimal(get_field_with_alternatives('pfcfRatioTTM', [
            'pfcfRatio', 'priceToFreeCashFlowRatio', 'priceFreeCashFlowRatio', 'priceToFCF', 'p/fcf', 'priceToFreeCashFlowTTM'
        ])),
        
        'pb_ratio_ttm': safe_decimal(get_field_with_alternatives('pbRatioTTM', [
            'pbRatio', 'priceToBookRatio', 'priceBookRatio', 'priceToBook', 'p/b', 'price/book', 'priceToBookRatioTTM'
        ])),
        
        'ptb_ratio_ttm': safe_decimal(get_field_with_alternatives('ptbRatioTTM', [
            'ptbRatio', 'priceToTangibleBookRatio', 'priceTangibleBookRatio', 'priceToTangibleBook'
        ])),
        
        # Enterprise value ratios - from both endpoints
        'ev_to_sales_ttm': safe_decimal(get_field_with_alternatives('evToSalesTTM', ['evToSales', 'enterpriseValueToSales', 'evSales'])),
        'enterprise_value_over_ebitdat_tm': safe_decimal(get_field_with_alternatives('enterpriseValueOverEBITDATTM', [
            'enterpriseValueOverEBITDA', 'evToEBITDA', 'evEbitda', 'evToEbitda', 'enterpriseValueMultipleTTM'
        ])),
        'ev_to_operating_cash_flow_ttm': safe_decimal(get_field_with_alternatives('evToOperatingCashFlowTTM', ['evToOperatingCashFlow', 'evOcf', 'evToCashflow'])),
        'ev_to_free_cash_flow_ttm': safe_decimal(get_field_with_alternatives('evToFreeCashFlowTTM', ['evToFreeCashFlow', 'evFcf', 'evToFcf'])),
        'earnings_yield_ttm': safe_decimal(get_field_with_alternatives('earningsYieldTTM', ['earningsYield'])),
        
        'free_cash_flow_yield_ttm': safe_decimal(get_field_with_alternatives('freeCashFlowYieldTTM', ['freeCashFlowYield'])),

        # Profitability Margins & Returns TTM - mainly from ratios-ttm
        'gross_profit_margin_ttm': safe_decimal(get_field_with_alternatives('grossProfitMarginTTM', ['grossProfitMargin', 'grossMargin'])),
        'operating_profit_margin_ttm': safe_decimal(get_field_with_alternatives('operatingProfitMarginTTM', ['operatingProfitMargin', 'operatingMargin', 'ebitMarginTTM'])),
        'pretax_profit_margin_ttm': safe_decimal(get_field_with_alternatives('pretaxProfitMarginTTM', ['pretaxProfitMargin', 'pretaxMargin'])),
        'net_profit_margin_ttm': safe_decimal(get_field_with_alternatives('netProfitMarginTTM', ['netProfitMargin', 'netMargin'])),
        
        # Returns - from ratios-ttm
        'roe_ttm': safe_decimal(get_field_with_alternatives('roeTTM', ['roe', 'returnOnEquity', 'returnOnEquityTTM'])),
        'return_on_tangible_assets_ttm': safe_decimal(get_field_with_alternatives('returnOnTangibleAssetsTTM', ['returnOnTangibleAssets', 'rota'])),
        'return_on_assets_ttm': safe_decimal(get_field_with_alternatives('returnOnAssetsTTM', ['returnOnAssets', 'roa'])),
        'roic_ttm': safe_decimal(get_field_with_alternatives('roicTTM', ['roic', 'returnOnInvestedCapital', 'returnOnInvestedCapitalTTM'])),
        'return_on_capital_employed_ttm': safe_decimal(get_field_with_alternatives('returnOnCapitalEmployedTTM', ['returnOnCapitalEmployed', 'roce'])),
        'income_quality_ttm': safe_decimal(get_field_with_alternatives('incomeQualityTTM', ['incomeQuality'])),

        # Debt, Coverage & Liquidity TTM
        'debt_to_equity_ttm': safe_decimal(get_field_with_alternatives('debtToEquityTTM', ['debtToEquity', 'debtEquityRatio', 'debtToEquityRatioTTM'])),
        'debt_to_assets_ttm': safe_decimal(get_field_with_alternatives('debtToAssetsTTM', ['debtToAssets', 'debtRatio', 'debtToAssetsRatioTTM'])),
        'net_debt_to_ebitdat_tm': safe_decimal(get_field_with_alternatives('netDebtToEBITDATTM', ['netDebtToEBITDA'])),
        'current_ratio_ttm': safe_decimal(get_field_with_alternatives('currentRatioTTM', ['currentRatio'])),
        'interest_coverage_ttm': safe_decimal(get_field_with_alternatives('interestCoverageTTM', [
            'interestCoverage', 'interestCoverageRatio', 'interestCoverageRatioTTM'
        ])),
        'long_term_debt_to_capitalization_ttm': safe_decimal(get_field_with_alternatives('longTermDebtToCapitalizationTTM', [
            'longTermDebtToCapitalization', 'longTermDebtToCapitalRatioTTM'
        ])),
        'total_debt_to_capitalization_ttm': safe_decimal(get_field_with_alternatives('totalDebtToCapitalizationTTM', [
            'totalDebtToCapitalization', 'debtToCapitalRatioTTM'
        ])),
        'debt_ratio_ttm': safe_decimal(get_field_with_alternatives('debtRatioTTM', [
            'debtRatio', 'debtToAssetsRatioTTM'
        ])),
        'cash_flow_to_debt_ratio_ttm': safe_decimal(get_field_with_alternatives('cashFlowToDebtRatioTTM', [
            'cashFlowToDebtRatio', 'operatingCashFlowToDebt', 'operatingCashFlowRatioTTM'
        ])),
        
        # More complex financial ratios - from ratios-ttm
        'company_equity_multiplier_ttm': safe_decimal(get_field_with_alternatives('companyEquityMultiplierTTM', [
            'companyEquityMultiplier', 'equityMultiplier', 'assetsToEquity', 'equityRatio', 'financialLeverageRatioTTM'
        ])),
        
        'cash_flow_coverage_ratios_ttm': safe_decimal(get_field_with_alternatives('cashFlowCoverageRatiosTTM', [
            'cashFlowCoverageRatios', 'cashFlowCoverage', 'operatingCashFlowCoverageRatio', 'operatingCashFlowCoverageRatioTTM'
        ])),
        
        'short_term_coverage_ratios_ttm': safe_decimal(get_field_with_alternatives('shortTermCoverageRatiosTTM', [
            'shortTermCoverageRatios', 'shortTermOperatingCashFlowCoverageRatioTTM'
        ])),
        'capital_expenditure_coverage_ratio_ttm': safe_decimal(get_field_with_alternatives('capitalExpenditureCoverageRatioTTM', [
            'capitalExpenditureCoverageRatio', 'capitalExpenditureCoverageRatioTTM'
        ])),

        # Efficiency & Turnover TTM
        'receivables_turnover_ttm': safe_decimal(get_field_with_alternatives('receivablesTurnoverTTM', [
            'receivablesTurnover', 'accountsReceivableTurnover', 'receivablesTurnoverTTM'
        ])),
        'payables_turnover_ttm': safe_decimal(get_field_with_alternatives('payablesTurnoverTTM', [
            'payablesTurnover', 'accountsPayableTurnover', 'payablesTurnoverTTM'
        ])),
        'inventory_turnover_ttm': safe_decimal(get_field_with_alternatives('inventoryTurnoverTTM', [
            'inventoryTurnover', 'inventoryTurnoverTTM'
        ])),
        'asset_turnover_ttm': safe_decimal(get_field_with_alternatives('assetTurnoverTTM', [
            'assetTurnover', 'assetTurnoverTTM'
        ])),
        'fixed_asset_turnover_ttm': safe_decimal(get_field_with_alternatives('fixedAssetTurnoverTTM', [
            'fixedAssetTurnover', 'fixedAssetTurnoverTTM'
        ])),

        # Dividends TTM
        'dividend_yield_ttm': safe_decimal(get_field_with_alternatives('dividendYieldTTM', ['dividendYield'])),
        
        # Dividend yield as percentage - from ratios-ttm
        'dividend_yield_percentage_ttm': safe_decimal(get_field_with_alternatives('dividendYieldPercentageTTM', [
            'dividendYieldPercentage', 'annualDividendYieldPercent', 'dividendYieldTTM', 'dividendRate'
        ])),
        
        # Payout ratio - from ratios-ttm 
        'payout_ratio_ttm': safe_decimal(get_field_with_alternatives('payoutRatioTTM', [
            'payoutRatio', 'dividendPayoutRatio', 'dividendPayout', 'dividendPayoutRatioTTM'
        ])),
        
        'dividend_paid_and_capex_coverage_ratio_ttm': safe_decimal(get_field_with_alternatives('dividendPaidAndCapexCoverageRatioTTM', [
            'dividendPaidAndCapexCoverageRatio', 'dividendPaidAndCapexCoverageRatioTTM'
        ])),

        # Capex & Expenses TTM
        'capex_to_operating_cash_flow_ttm': safe_decimal(get_field_with_alternatives('capexToOperatingCashFlowTTM', [
            'capexToOperatingCashFlow', 'capexToOperatingCashFlowTTM'
        ])),
        'capex_to_revenue_ttm': safe_decimal(get_field_with_alternatives('capexToRevenueTTM', ['capexToRevenue'])),
        'capex_to_depreciation_ttm': safe_decimal(get_field_with_alternatives('capexToDepreciationTTM', ['capexToDepreciation'])),
        'sales_general_and_administrative_to_revenue_ttm': safe_decimal(get_field_with_alternatives('salesGeneralAndAdministrativeToRevenueTTM', [
            'salesGeneralAndAdministrativeToRevenue', 'sgaToRevenue'
        ])),
        'research_and_developement_to_revenue_ttm': safe_decimal(get_field_with_alternatives('researchAndDevelopementToRevenueTTM', [
            'researchAndDevelopementToRevenue', 'rndToRevenue', 'researchAndDevelopementToRevenueTTM'
        ])),
        'stock_based_compensation_to_revenue_ttm': safe_decimal(get_field_with_alternatives('stockBasedCompensationToRevenueTTM', [
            'stockBasedCompensationToRevenue'
        ])),

        # Other Metrics TTM
        'graham_number_ttm': safe_decimal(get_field_with_alternatives('grahamNumberTTM', ['grahamNumber'])),
        'working_capital_ttm': safe_int(get_field_with_alternatives('workingCapitalTTM', ['workingCapital'])),
        'intangibles_to_total_assets_ttm': safe_decimal(get_field_with_alternatives('intangiblesToTotalAssetsTTM', ['intangiblesToTotalAssets'])),
        'invested_capital_ttm': safe_int(get_field_with_alternatives('investedCapitalTTM', ['investedCapital'])),
        'tangible_asset_value_ttm': safe_int(get_field_with_alternatives('tangibleAssetValueTTM', ['tangibleAssetValue', 'tangibleAssets'])),
        'net_current_asset_value_ttm': safe_int(get_field_with_alternatives('netCurrentAssetValueTTM', ['netCurrentAssetValue'])),
        'graham_net_net_ttm': safe_decimal(get_field_with_alternatives('grahamNetNetTTM', ['grahamNetNet'])),
        'average_receivables_ttm': safe_int(get_field_with_alternatives('averageReceivablesTTM', ['averageReceivables'])),
        'average_payables_ttm': safe_int(get_field_with_alternatives('averagePayablesTTM', ['averagePayables'])),
        'average_inventory_ttm': safe_int(get_field_with_alternatives('averageInventoryTTM', ['averageInventory'])),
        
        # Days metrics - calculated from turnover ratios if needed
        'days_sales_outstanding_ttm': safe_decimal(get_field_with_alternatives('daysSalesOutstandingTTM', [
            'daysSalesOutstanding', 'dso', 'averageCollectionPeriod', 'daysSalesInReceivables'
        ])),
        
        'days_payables_outstanding_ttm': safe_decimal(get_field_with_alternatives('daysPayablesOutstandingTTM', [
            'daysPayablesOutstanding', 'dpo', 'averagePaymentPeriod', 'daysPayablesInPayables'
        ])),
        
        'days_of_inventory_on_hand_ttm': safe_decimal(get_field_with_alternatives('daysOfInventoryOnHandTTM', [
            'daysOfInventoryOnHand', 'doh', 'inventoryDays', 'daysInventory', 'daysInventoryOutstanding', 
            'daysOfInventoryOnHandTTM'
        ])),
        
        'operating_cash_flow_sales_ratio_ttm': safe_decimal(get_field_with_alternatives('operatingCashFlowSalesRatioTTM', [
            'operatingCashFlowSalesRatio', 'operatingCashFlowSalesRatioTTM'
        ])),
        'free_cash_flow_operating_cash_flow_ratio_ttm': safe_decimal(get_field_with_alternatives('freeCashFlowOperatingCashFlowRatioTTM', [
            'freeCashFlowOperatingCashFlowRatio', 'freeCashFlowOperatingCashFlowRatioTTM'
        ]))
    }
    
    # Try calculating any missing metrics based on other available data
    # These calculations may not be perfectly aligned with FMP's methodology
    
    # 1. Calculate missing returns metrics
    # Calculate ROE if missing (Net Income / Shareholders Equity)
    if ttm_metrics['roe_ttm'] is None:
        net_income = safe_decimal(get_field_with_alternatives('netIncome', ['netIncomeAnnual', 'netIncomeTTM']))
        shareholders_equity = safe_decimal(get_field_with_alternatives('shareholdersEquity', ['totalShareholdersEquity', 'totalEquity']))
        if net_income is not None and shareholders_equity is not None and shareholders_equity != 0:
            ttm_metrics['roe_ttm'] = net_income / shareholders_equity
            logger.info(f"Calculated roe_ttm for {symbol}")
            
    # Calculate ROIC if missing (NOPAT / Invested Capital)
    if ttm_metrics['roic_ttm'] is None:
        ebit = safe_decimal(get_field_with_alternatives('ebit', ['ebitTTM', 'operatingIncome']))
        tax_rate = safe_decimal(get_field_with_alternatives('effectiveTaxRate', ['taxRate']))
        if tax_rate is None:
            # Default tax rate approximation if not available
            tax_rate = 0.25
            
        invested_capital = safe_decimal(get_field_with_alternatives('investedCapital', ['totalDebt', 'totalEquity']))
        
        if ebit is not None and invested_capital is not None and invested_capital != 0:
            nopat = ebit * (1 - tax_rate)
            ttm_metrics['roic_ttm'] = nopat / invested_capital
            logger.info(f"Calculated roic_ttm for {symbol}")
    
    # 2. Calculate debt ratios if missing
    # Calculate debt_to_equity_ttm if missing
    if ttm_metrics['debt_to_equity_ttm'] is None:
        total_debt = safe_decimal(get_field_with_alternatives('totalDebt', ['debt', 'longTermDebt', 'shortTermDebt']))
        shareholders_equity = safe_decimal(get_field_with_alternatives('shareholdersEquity', ['totalShareholdersEquity', 'totalEquity']))
        
        if total_debt is not None and shareholders_equity is not None and shareholders_equity != 0:
            ttm_metrics['debt_to_equity_ttm'] = total_debt / shareholders_equity
            logger.info(f"Calculated debt_to_equity_ttm for {symbol}")
    
    # Calculate debt_to_assets_ttm if missing
    if ttm_metrics['debt_to_assets_ttm'] is None:
        total_debt = safe_decimal(get_field_with_alternatives('totalDebt', ['debt', 'longTermDebt', 'shortTermDebt']))
        total_assets = safe_decimal(get_field_with_alternatives('totalAssets', ['assets']))
        
        if total_debt is not None and total_assets is not None and total_assets != 0:
            ttm_metrics['debt_to_assets_ttm'] = total_debt / total_assets
            logger.info(f"Calculated debt_to_assets_ttm for {symbol}")
    
    # Calculate debt_ratio_ttm if missing (this is often the same as debt_to_assets)
    if ttm_metrics['debt_ratio_ttm'] is None and ttm_metrics['debt_to_assets_ttm'] is not None:
        ttm_metrics['debt_ratio_ttm'] = ttm_metrics['debt_to_assets_ttm']
        logger.info(f"Using debt_to_assets_ttm as debt_ratio_ttm for {symbol}")
    
    # 3. Calculate capitalization ratios
    # Calculate long_term_debt_to_capitalization_ttm if missing
    if ttm_metrics['long_term_debt_to_capitalization_ttm'] is None:
        long_term_debt = safe_decimal(get_field_with_alternatives('longTermDebt', ['longTermDebts']))
        long_term_debt_plus_equity = safe_decimal(get_field_with_alternatives('longTermDebtToCapitalization', ['longTermDebtPlusEquity']))
        shareholders_equity = safe_decimal(get_field_with_alternatives('shareholdersEquity', ['totalShareholdersEquity', 'totalEquity']))
        
        # Try to calculate if we have the components
        if long_term_debt is not None and shareholders_equity is not None:
            capitalization = long_term_debt + shareholders_equity
            if capitalization != 0:
                ttm_metrics['long_term_debt_to_capitalization_ttm'] = long_term_debt / capitalization
                logger.info(f"Calculated long_term_debt_to_capitalization_ttm for {symbol}")
        elif long_term_debt_plus_equity is not None and long_term_debt is not None and long_term_debt_plus_equity != 0:
            ttm_metrics['long_term_debt_to_capitalization_ttm'] = long_term_debt / long_term_debt_plus_equity
            logger.info(f"Calculated long_term_debt_to_capitalization_ttm from debt/capital for {symbol}")
    
    # Calculate total_debt_to_capitalization_ttm if missing
    if ttm_metrics['total_debt_to_capitalization_ttm'] is None:
        total_debt = safe_decimal(get_field_with_alternatives('totalDebt', ['debt']))
        shareholders_equity = safe_decimal(get_field_with_alternatives('shareholdersEquity', ['totalShareholdersEquity', 'totalEquity']))
        
        if total_debt is not None and shareholders_equity is not None:
            capitalization = total_debt + shareholders_equity
            if capitalization != 0:
                ttm_metrics['total_debt_to_capitalization_ttm'] = total_debt / capitalization
                logger.info(f"Calculated total_debt_to_capitalization_ttm for {symbol}")
    
    # 4. Calculate coverage ratios
    # Calculate interest_coverage_ttm if missing
    if ttm_metrics['interest_coverage_ttm'] is None:
        ebit = safe_decimal(get_field_with_alternatives('ebit', ['ebitTTM', 'operatingIncome']))
        interest_expense = safe_decimal(get_field_with_alternatives('interestExpense', ['interestExpenseTTM', 'interestPaid']))
        
        if ebit is not None and interest_expense is not None and interest_expense != 0:
            ttm_metrics['interest_coverage_ttm'] = ebit / abs(interest_expense)
            logger.info(f"Calculated interest_coverage_ttm for {symbol}")
    
    # Calculate cash_flow_to_debt_ratio_ttm if missing
    if ttm_metrics['cash_flow_to_debt_ratio_ttm'] is None:
        operating_cash_flow = safe_decimal(get_field_with_alternatives('operatingCashFlow', ['operatingCashFlowTTM']))
        total_debt = safe_decimal(get_field_with_alternatives('totalDebt', ['debt', 'longTermDebt', 'shortTermDebt']))
        
        if operating_cash_flow is not None and total_debt is not None and total_debt != 0:
            ttm_metrics['cash_flow_to_debt_ratio_ttm'] = operating_cash_flow / total_debt
            logger.info(f"Calculated cash_flow_to_debt_ratio_ttm for {symbol}")
    
    # Calculate company_equity_multiplier_ttm if missing (Assets/Equity)
    if ttm_metrics['company_equity_multiplier_ttm'] is None:
        total_assets = safe_decimal(get_field_with_alternatives('totalAssets', ['assets']))
        total_equity = safe_decimal(get_field_with_alternatives('totalEquity', ['totalShareholdersEquity', 'shareholdersEquity']))
        if total_assets is not None and total_equity is not None and total_equity != 0:
            ttm_metrics['company_equity_multiplier_ttm'] = total_assets / total_equity
            logger.info(f"Calculated company_equity_multiplier_ttm for {symbol} from assets/equity")
    
    # Calculate cash_flow_coverage_ratios_ttm if missing
    if ttm_metrics['cash_flow_coverage_ratios_ttm'] is None:
        operating_cash_flow = safe_decimal(get_field_with_alternatives('operatingCashFlow', ['operatingCashFlowTTM']))
        capital_expenditure = safe_decimal(get_field_with_alternatives('capitalExpenditure', ['capitalExpenditureTTM']))
        debt_repayment = safe_decimal(get_field_with_alternatives('debtRepayment', ['debtRepaymentTTM']))
        
        # If we have OCF and at least one of the other components
        if operating_cash_flow is not None and (capital_expenditure is not None or debt_repayment is not None):
            denominator = 0
            if capital_expenditure is not None:
                denominator += abs(capital_expenditure)
            if debt_repayment is not None:
                denominator += abs(debt_repayment)
                
            if denominator != 0:
                ttm_metrics['cash_flow_coverage_ratios_ttm'] = operating_cash_flow / denominator
                logger.info(f"Calculated cash_flow_coverage_ratios_ttm for {symbol}")
    
    # Calculate short_term_coverage_ratios_ttm if missing (Current Assets / Current Liabilities)
    if ttm_metrics['short_term_coverage_ratios_ttm'] is None and ttm_metrics['current_ratio_ttm'] is not None:
        # Short term coverage is often the same as current ratio
        ttm_metrics['short_term_coverage_ratios_ttm'] = ttm_metrics['current_ratio_ttm']
        logger.info(f"Using current_ratio_ttm as short_term_coverage_ratios_ttm for {symbol}")
    elif ttm_metrics['short_term_coverage_ratios_ttm'] is None:
        current_assets = safe_decimal(get_field_with_alternatives('currentAssets', ['totalCurrentAssets']))
        current_liabilities = safe_decimal(get_field_with_alternatives('currentLiabilities', ['totalCurrentLiabilities']))
        
        if current_assets is not None and current_liabilities is not None and current_liabilities != 0:
            ttm_metrics['short_term_coverage_ratios_ttm'] = current_assets / current_liabilities
            logger.info(f"Calculated short_term_coverage_ratios_ttm for {symbol}")
    
    # 5. Calculate dividend metrics if missing
    # Convert dividend_yield_ttm to percentage if needed
    if ttm_metrics['dividend_yield_percentage_ttm'] is None and ttm_metrics['dividend_yield_ttm'] is not None:
        # Convert from decimal to percentage (multiply by 100)
        ttm_metrics['dividend_yield_percentage_ttm'] = ttm_metrics['dividend_yield_ttm'] * 100
        logger.info(f"Calculated dividend_yield_percentage_ttm for {symbol} from dividend_yield_ttm")
    
    # Calculate payout_ratio if missing (Dividends per Share / EPS)
    if ttm_metrics['payout_ratio_ttm'] is None:
        dividend_per_share = safe_decimal(get_field_with_alternatives('dividendPerShare', ['dividendPayoutPerShare', 'dividends']))
        eps = safe_decimal(get_field_with_alternatives('eps', ['earningsPerShare', 'netIncomePerShare']))
        
        if dividend_per_share is not None and eps is not None and eps != 0:
            ttm_metrics['payout_ratio_ttm'] = dividend_per_share / eps
            logger.info(f"Calculated payout_ratio_ttm for {symbol} from dividendPerShare/eps")
        elif dividend_per_share is not None and ttm_metrics['net_income_per_share_ttm'] is not None and ttm_metrics['net_income_per_share_ttm'] != 0:
            ttm_metrics['payout_ratio_ttm'] = dividend_per_share / ttm_metrics['net_income_per_share_ttm']
            logger.info(f"Calculated payout_ratio_ttm for {symbol} using net_income_per_share_ttm")
        
    # 6. Calculate days metrics from turnover if missing
    if ttm_metrics['days_sales_outstanding_ttm'] is None and ttm_metrics['receivables_turnover_ttm'] is not None and ttm_metrics['receivables_turnover_ttm'] != 0:
        ttm_metrics['days_sales_outstanding_ttm'] = 365 / ttm_metrics['receivables_turnover_ttm']
        logger.info(f"Calculated days_sales_outstanding_ttm for {symbol} from receivables_turnover_ttm")
        
    if ttm_metrics['days_payables_outstanding_ttm'] is None and ttm_metrics['payables_turnover_ttm'] is not None and ttm_metrics['payables_turnover_ttm'] != 0:
        ttm_metrics['days_payables_outstanding_ttm'] = 365 / ttm_metrics['payables_turnover_ttm']
        logger.info(f"Calculated days_payables_outstanding_ttm for {symbol} from payables_turnover_ttm")
        
    if ttm_metrics['days_of_inventory_on_hand_ttm'] is None and ttm_metrics['inventory_turnover_ttm'] is not None and ttm_metrics['inventory_turnover_ttm'] != 0:
        ttm_metrics['days_of_inventory_on_hand_ttm'] = 365 / ttm_metrics['inventory_turnover_ttm']
        logger.info(f"Calculated days_of_inventory_on_hand_ttm for {symbol} from inventory_turnover_ttm")
    
    # Filter out None values before returning if you want cleaner DB records (optional)
    # return {k: v for k, v in ttm_metrics.items() if v is not None}
    return ttm_metrics

# 5. Calculated Metrics - No parser needed, data is calculated internally
# --- Analyst ratings ----------------------------------------------------------
from datetime import date

def parse_analyst_rating(api_data: Dict[str, Any], source: str) -> Optional[Dict[str, Any]]:
    """
    Normalise *any* FMP analyst / price‑target / grades payload so it fits
    the analyst_ratings table.  We only return columns that exist in the table.
    """

    if not api_data or not api_data.get("symbol"):
        logger.warning("Analyst payload is missing 'symbol' – skip: %s", api_data)
        return None

    # ── date ────────────────────────────────────────────────────────────────────
    raw_date = (
        api_data.get("date")
        or api_data.get("publishedDate")          # price‑target / news endpoints
        or date.today().isoformat()
    )
    # keep only the YYYY‑MM‑DD part so it matches the column type (DATE)
    record_date = raw_date[:10]

    record: Dict[str, Any] = {
        # primary‑key columns
        "symbol"  : api_data["symbol"],
        "date"    : record_date,
        "source"  : source,

        # free‑text firm / action fields
        "rating_analyst_firm" : api_data.get("gradingCompany")
                                or api_data.get("analystCompany")
                                or source,  # fallback to endpoint as firm identifier
        "rating_previous"     : api_data.get("previousGrade")
                                or api_data.get("ratingScalePrevious"),
        "rating_current"      : api_data.get("newGrade")
                                or api_data.get("ratingScaleCurrent")
                                or api_data.get("rating"),
        "rating_action"       : api_data.get("action")
                                or api_data.get("ratingRecommendation"),

        # detail scores (ratings‑snapshot)
        "rating_dcf_score" : safe_decimal(api_data.get("discountedCashFlowScore")),
        "rating_roe_score" : safe_decimal(api_data.get("returnOnEquityScore")),
        "rating_roa_score" : safe_decimal(api_data.get("returnOnAssetsScore")),
        "rating_de_score"  : safe_decimal(api_data.get("debtToEquityScore")),
        "rating_pe_score"  : safe_decimal(api_data.get("priceToEarningsScore")),
        "rating_pb_score"  : safe_decimal(api_data.get("priceToBookScore")),

        # price‑target consensus
        "price_target_consensus" : safe_decimal(api_data.get("targetConsensus")),
        "price_target_high"      : safe_decimal(api_data.get("targetHigh")),
        "price_target_low"       : safe_decimal(api_data.get("targetLow")),
        "price_target_median"    : safe_decimal(api_data.get("targetMedian")),

        # price‑target / grade news
        "price_when_posted" : safe_decimal(
                                api_data.get("priceWhenPosted")
                                or api_data.get("stockPrice")
                              ),
        "news_url"       : api_data.get("url") or api_data.get("newsURL"),
        "news_publisher" : api_data.get("publisher") or api_data.get("newsPublisher"),
        "news_title"     : api_data.get("title")     or api_data.get("newsTitle"),

        # grades‑consensus
        "consensus_strong_buy"  : safe_int(api_data.get("strongBuy")),
        "consensus_buy"         : safe_int(api_data.get("buy")),
        "consensus_hold"        : safe_int(api_data.get("hold")),
        "consensus_sell"        : safe_int(api_data.get("sell")),
        "consensus_strong_sell" : safe_int(api_data.get("strongSell")),
    }

    # remove keys whose value is *all* None / "" so we never send extras
    record = {k: v for k, v in record.items() if v not in (None, "", [])}

    # must have at least **one** rating‑related field or target, otherwise skip
    if not any(k.startswith(("rating_", "price_target_", "consensus_")) for k in record):
        logger.debug("Analyst payload had no useful fields – skip: %s", api_data)
        return None

    return record

# 7. Stock News
def parse_stock_news(api_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Parses an individual stock news item from FMP API.
    
    Args:
        api_data: Raw API response data for a single news item
        
    Returns:
        Parsed news item ready for database insertion, or None if invalid
    """
    if not api_data or not isinstance(api_data, dict):
        logger.warning(f"Invalid news data format: {api_data}")
        return None
    
    # Required fields - if any of these are missing, we skip the item
    required_fields = ['symbol', 'title', 'publishedDate']
    for field in required_fields:
        if field not in api_data or not api_data[field]:
            logger.warning(f"News item missing required field: {field}")
            return None
    
    # Parse the item - match EXACT field names from the database schema
    news_item = {
        'symbol': api_data.get('symbol'),
        'title': api_data.get('title'),
        'image_url': api_data.get('image', ''),  # renamed from 'image' to 'image_url'
        'site': api_data.get('site', ''),
        'text': api_data.get('text', ''),
        'source_url': api_data.get('url', ''),   # renamed from 'url' to 'source_url'
        'published_date': api_data.get('publishedDate')
        # Removed 'summary' field - not in the database schema
    }
    
    return news_item

def parse_stock_news_list(api_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Parses a list of stock news items from FMP API.
    
    Args:
        api_data_list: Raw API response data containing multiple news items
        
    Returns:
        List of parsed news items ready for database insertion
    """
    if not api_data_list or not isinstance(api_data_list, list):
        logger.warning(f"Invalid news data list format: {api_data_list}")
        return []
    
    parsed_items = []
    for item in api_data_list:
        try:
            parsed = parse_stock_news(item)
            if parsed:
                parsed_items.append(parsed)
        except Exception as e:
            logger.warning(f"Error parsing news item: {e}")
            # Continue with the next item
    
    return parsed_items

# 8. ESG Scores Historical
def parse_esg_historical(api_data: Dict[str, Any], symbol: str, source: str) -> Optional[Dict[str, Any]]:
    """Parses FMP ESG data (/esg-ratings, /esg-disclosures) into 'esg_scores_historical' format."""
    if not api_data:
        logger.warning(f"Received empty ESG data for {symbol} from {source}: {api_data}")
        return None
    # Determine report_date: prefer 'date', else use fiscalYear/calendarYear as year-end
    raw_date = api_data.get('date')
    if raw_date:
        date_str = raw_date.rstrip('Z')
    else:
        fy = api_data.get('fiscalYear') or api_data.get('calendarYear')
        if fy:
            date_str = f"{fy}-12-31"
        else:
            logger.warning(f"Missing date info in ESG data for {symbol} from {source}: {api_data}")
            return None
    try:
        dt = datetime.fromisoformat(date_str)
    except Exception:
        logger.warning(f"Invalid report_date in ESG data for {symbol} from {source}: {date_str}")
        return None
    # Determine calendar_year: use calendarYear/fiscalYear if present, fallback to dt.year
    raw_year = api_data.get('calendarYear') or api_data.get('fiscalYear')
    year = safe_int(raw_year) if raw_year is not None else None
    if year is None:
        year = dt.year
    esg_record = {
        'symbol': symbol,
        'report_date': dt.date().isoformat(),
        'calendar_year': year,
        'esg_score': safe_decimal(api_data.get('ESGScore') or api_data.get('esgScore')),
        'environmental_score': safe_decimal(api_data.get('environmentalScore')),
        'social_score': safe_decimal(api_data.get('socialScore')),
        'governance_score': safe_decimal(api_data.get('governanceScore')),
        'esg_rating_grade': api_data.get('ESGRiskRating') or api_data.get('rating') or api_data.get('grade'),
        'data_source': source
    }
    return esg_record

def parse_political_disclosure(api_data: Dict[str, Any], source: str) -> Optional[Dict[str, Any]]:
    """Parses FMP Senate/House trades API data into 'political_disclosures' format."""
    if not api_data:
        logger.warning(f"Empty political disclosure data from {source}: {api_data}")
        return None
    link = api_data.get('link')
    if not link:
        logger.warning(f"Missing link in political disclosure: {api_data}")
        return None
    try:
        rec = {
            'source': source,
            'first_name': api_data.get('firstName'),
            'last_name': api_data.get('lastName'),
            'office': api_data.get('office'),
            'district': api_data.get('district'),
            'disclosure_date': api_data.get('disclosureDate'),
            'transaction_date': api_data.get('transactionDate'),
            'owner_type': api_data.get('owner'),
            'ticker': api_data.get('symbol'),
            'asset_description': api_data.get('assetDescription'),
            'asset_type': api_data.get('assetType'),
            'transaction_type': api_data.get('type'),
            'amount_range': api_data.get('amount'),
            'capital_gains_over_200_usd': str(api_data.get('capitalGainsOver200USD')).lower() == 'true',
            'comment': api_data.get('comment') or None,
            'ptr_link': link,
        }
    except Exception as e:
        logger.warning(f"Error parsing political disclosure data: {e} - {api_data}")
        return None
    return rec

# 9. Dividends
def parse_dividend(api_data: Dict[str, Any], symbol: str) -> Optional[Dict[str, Any]]:
    """Parses FMP Dividend data (/dividends/{symbol}) into 'dividends' table format."""
    date_str = api_data.get('date')
    if not api_data or not date_str:
        logger.warning(f"Received incomplete dividend data for {symbol}: {api_data}")
        return None
    # Only include non-empty date fields
    record = {
        'symbol': symbol,
        'date': date_str,
        'label': api_data.get('label'),
        'adj_dividend': safe_decimal(api_data.get('adjDividend')),
        'dividend': safe_decimal(api_data.get('dividend')),
        'yield': safe_decimal(api_data.get('yield')),
        'record_date': api_data.get('recordDate') or None,
        'payment_date': api_data.get('paymentDate') or None,
        'declaration_date': api_data.get('declarationDate') or None
    }
    # Basic check: must have a dividend amount
    if record['dividend'] is None and record['adj_dividend'] is None:
        logger.warning(f"Skipping dividend record for {symbol} on {record['date']} due to missing amount.")
        return None
    return record

# 10. Insider Trading Statistics
def parse_insider_trading_stats(api_data: Dict[str, Any], symbol: str) -> Optional[Dict[str, Any]]:
    """Parses FMP Insider Trading Statistics API data into 'insider_trades' format."""
    year = api_data.get('year')
    quarter = api_data.get('quarter')
    if year is None or quarter is None:
        logger.warning(f"Received incomplete insider stats for {symbol}: {api_data}")
        return None
    record = {
        'symbol': symbol,
        'stats_company_cik': api_data.get('cik'),
        'stats_year': safe_int(year),
        'stats_quarter': safe_int(quarter),
        'acquired_transactions': safe_int(api_data.get('acquiredTransactions')),
        'disposed_transactions': safe_int(api_data.get('disposedTransactions')),
        'acquired_disposed_ratio': safe_decimal(api_data.get('acquiredDisposedRatio')),
        'total_acquired': safe_int(api_data.get('totalAcquired')),
        'total_disposed': safe_int(api_data.get('totalDisposed')),
        'average_acquired': safe_decimal(api_data.get('averageAcquired')),
        'average_disposed': safe_decimal(api_data.get('averageDisposed')),
        'total_purchases': safe_int(api_data.get('totalPurchases')),
        'total_sales': safe_int(api_data.get('totalSales'))
    }
    return record

# 11. Financial Estimates
def parse_financial_estimate(api_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Parses FMP Financial Estimate data (/analyst-estimates/{symbol}) into 'financial_estimates' format."""
    if not api_data or not api_data.get('symbol') or not api_data.get('date'): # 'date' is usually publish date
        logger.warning(f"Received incomplete financial estimate data: {api_data}")
        return None

    # Determine report_period (default to FY if missing/invalid)
    period_val = api_data.get('period') or 'FY'
    if period_val not in ['Q1', 'Q2', 'Q3', 'Q4', 'FY']:
        logger.debug(f"Invalid estimate period '{period_val}' for {api_data.get('symbol')}, defaulting to 'FY'")
        period_val = 'FY'

    estimate_record = {
        'symbol': api_data.get('symbol'),
        'publish_date': date.today().isoformat(),
        'fiscal_date_ending': api_data.get('date'),
        'report_period_year': safe_int(api_data.get('calendarYear') or api_data.get('year')), # Use calendarYear if available
        'report_period': period_val,

        'estimated_revenue_avg': safe_int(api_data.get('revenueAvg')),
        'estimated_revenue_low': safe_int(api_data.get('revenueLow')),
        'estimated_revenue_high': safe_int(api_data.get('revenueHigh')),
        'estimated_revenue_analyst_count': safe_int(api_data.get('numAnalystsRevenue')),

        'estimated_eps_avg': safe_decimal(api_data.get('epsAvg')),
        'estimated_eps_low': safe_decimal(api_data.get('epsLow')),
        'estimated_eps_high': safe_decimal(api_data.get('epsHigh')),
        'estimated_eps_analyst_count': safe_int(api_data.get('numAnalystsEps')),

        'estimated_ebitda_avg': safe_int(api_data.get('ebitdaAvg')),
        'estimated_ebitda_low': safe_int(api_data.get('ebitdaLow')),
        'estimated_ebitda_high': safe_int(api_data.get('ebitdaHigh')),
        'estimated_ebitda_analyst_count': safe_int(api_data.get('numAnalystsRevenue')),

        'estimated_ebit_avg': safe_int(api_data.get('ebitAvg')),
        'estimated_ebit_low': safe_int(api_data.get('ebitLow')),
        'estimated_ebit_high': safe_int(api_data.get('ebitHigh')),
        'estimated_ebit_analyst_count': safe_int(api_data.get('numAnalystsRevenue')),

        'estimated_net_income_avg': safe_int(api_data.get('netIncomeAvg')),
        'estimated_net_income_low': safe_int(api_data.get('netIncomeLow')),
        'estimated_net_income_high': safe_int(api_data.get('netIncomeHigh')),
        'estimated_net_income_analyst_count': safe_int(api_data.get('numAnalystsRevenue')),

        'estimated_sga_expense_avg': safe_int(api_data.get('sgaExpenseAvg')),
        'estimated_sga_expense_low': safe_int(api_data.get('sgaExpenseLow')),
        'estimated_sga_expense_high': safe_int(api_data.get('sgaExpenseHigh')),
        'estimated_sga_expense_analyst_count': safe_int(api_data.get('numAnalystsRevenue')),

        'estimated_gross_profit_avg': safe_int(api_data.get('grossProfitAvg')),
        'estimated_gross_profit_low': safe_int(api_data.get('grossProfitLow')),
        'estimated_gross_profit_high': safe_int(api_data.get('grossProfitHigh')),
        'estimated_gross_profit_analyst_count': safe_int(api_data.get('numAnalystsRevenue')),
    }
    return estimate_record

# 12. Earnings Reports
def parse_earnings_report(api_data: Dict[str, Any], symbol: str) -> Optional[Dict[str, Any]]:
    """Parses FMP Earnings Report API data (/earnings) into 'earnings_reports' format."""
    date_str = api_data.get('date')
    if not api_data or not date_str:
        logger.warning(f"Received incomplete earnings data for {symbol}: {api_data}")
        return None
    try:
        dt = datetime.fromisoformat(date_str)
    except Exception:
        logger.warning(f"Invalid earnings date format for {symbol}: {date_str}")
        return None
    record = {
        'symbol': symbol,
        'date': dt.date().isoformat(),
        'quarter': (dt.month - 1) // 3 + 1,
        'year': dt.year,
        'eps': safe_decimal(api_data.get('epsActual')),
        'eps_estimated': safe_decimal(api_data.get('epsEstimated')),
        'revenue': safe_decimal(api_data.get('revenueActual')),
        'revenue_estimated': safe_decimal(api_data.get('revenueEstimated')),
        'time': api_data.get('time') or None
    }
    return record

# 13. Press Releases
def parse_press_release(api_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Parses FMP Press Release data into 'press_releases' format."""
    if not api_data or not api_data.get('title') or not api_data.get('date'):
        logger.warning(f"Received incomplete press release data: {api_data}")
        return None
        
    # Use a dummy URL if none provided for uniqueness, although API should provide one
    source_url = api_data.get('url', f"missing_url_{api_data.get('symbol', 'general')}_{api_data.get('date')}")
    if not source_url.startswith(('http://', 'https://')):
        # Handle potential relative URLs if needed, or assume absolute
        logger.warning(f"Press release URL may not be absolute: {source_url}")

    # Make sure we match the exact column names from the database schema
    release_record = {
        'symbol': api_data.get('symbol'),  # Could be None for general releases
        'published_date': api_data.get('date'),  # Map 'date' from API to 'published_date' in DB
        'title': api_data.get('title'),
        'text': api_data.get('text'),
        'source_url': source_url
    }
    return release_record

# 14. Financial Statement Growth
def parse_statement_growth(api_data: Dict[str, Any], symbol: str, statement_type: str) -> Optional[Dict[str, Any]]:
    """Parses FMP Statement Growth data into 'financial_statement_growth' format."""
    if not api_data or not api_data.get('date') or not api_data.get('period'):
        logger.warning(f"Received incomplete statement growth data for {symbol}, type {statement_type}: {api_data}")
        return None
    period_val = safe_text(api_data.get('period', '')).lower()
    if period_val not in ['annual', 'quarter']:
         logger.warning(f"Invalid period value '{period_val}' found for {symbol} growth statement. Skipping record.")
         return None

    growth_record = {
        'symbol': symbol,
        'report_date': api_data.get('date'),
        'period': period_val,
        'statement_type': statement_type.lower(),
        'calendar_year': safe_int(api_data.get('calendarYear')),
        'data': api_data # Store the original growth JSON
    }
    return growth_record

# 15. Key Metrics Historical
def parse_key_metrics_historical(api_data: Dict[str, Any], symbol: str) -> Optional[Dict[str, Any]]:
    """Parses FMP Historical Key Metrics data (/key-metrics/{symbol}) into 'key_metrics_historical' format."""
    if not api_data or not api_data.get('date') or not api_data.get('period'):
        logger.warning(f"Received incomplete historical key metrics data for {symbol}: {api_data}")
        return None
    period_val = safe_text(api_data.get('period', '')).lower()
    if period_val not in ['annual', 'quarter']:
         logger.warning(f"Invalid period value '{period_val}' found for {symbol} historical metrics. Skipping record.")
         return None

    record = {
        'symbol': symbol,
        'report_date': api_data.get('date'),
        'period': period_val,
        'calendar_year': safe_int(api_data.get('calendarYear')),
        'data': api_data # Store the original metrics JSON
    }
    return record

# 16. Financial Ratios Historical
def parse_financial_ratios_historical(api_data: Dict[str, Any], symbol: str) -> Optional[Dict[str, Any]]:
    """Parses FMP Historical Financial Ratios data (/ratios/{symbol}) into 'financial_ratios_historical' format."""
    if not api_data or not api_data.get('date') or not api_data.get('period'):
        logger.warning(f"Received incomplete historical ratios data for {symbol}: {api_data}")
        return None
    period_val = safe_text(api_data.get('period', '')).lower()
    if period_val not in ['annual', 'quarter']:
         logger.warning(f"Invalid period value '{period_val}' found for {symbol} historical ratios. Skipping record.")
         return None

    record = {
        'symbol': symbol,
        'report_date': api_data.get('date'),
        'period': period_val,
        'calendar_year': safe_int(api_data.get('calendarYear')),
        'data': api_data # Store the original ratios JSON
    }
    return record

# 17. FMP Financial Scores Historical
def parse_fmp_financial_score(api_data: Dict[str, Any], symbol: str) -> Optional[Dict[str, Any]]:
    """Parses FMP Financial Score data (/financial-scores/{symbol}) into 'fmp_financial_scores_historical' format."""
    if not api_data or not api_data.get('date'): # Need date for historical table
        logger.warning(f"Received incomplete financial score data for {symbol}: {api_data}")
        return None

    record = {
        'symbol': symbol,
        'date': api_data.get('date'),
        'altman_z_score': safe_decimal(api_data.get('altmanZScore')),
        'piotroski_score': safe_int(api_data.get('piotroskiScore'))
    }
    return record

# 18. Owner Earnings Historical
def parse_owner_earnings(api_data: Dict[str, Any], symbol: str) -> Optional[Dict[str, Any]]:
    """Parses FMP Owner Earnings data (/owner-earnings/{symbol}) into 'owner_earnings_historical' format."""
    if not api_data or not api_data.get('date'):
        logger.warning(f"Received incomplete owner earnings data for {symbol}: {api_data}")
        return None
    # FMP doesn't explicitly state 'period' for owner earnings, infer based on date/year?
    # Assuming it's annual if period isn't present. Adjust if FMP provides period.
    period_val = safe_text(api_data.get('period', 'annual')).lower() # Default to annual if missing
    if period_val not in ['annual', 'quarter']:
        period_val = 'annual'

    record = {
        'symbol': symbol,
        'date': api_data.get('date'),
        'period': period_val,
        'calendar_year': safe_int(api_data.get('calendarYear')),
        'owner_earnings': safe_int(api_data.get('ownerEarnings')) # Assuming integer/bigint makes sense
    }
    return record

# 19. Enterprise Values Historical
def parse_enterprise_value(api_data: Dict[str, Any], symbol: str) -> Optional[Dict[str, Any]]:
    """Parses FMP Enterprise Value data (/enterprise-values/{symbol}) into 'enterprise_values_historical' format."""
    if not api_data or not api_data.get('date') or not api_data.get('period'):
        logger.warning(f"Received incomplete enterprise value data for {symbol}: {api_data}")
        return None
    period_val = safe_text(api_data.get('period', '')).lower()
    if period_val not in ['annual', 'quarter']:
         logger.warning(f"Invalid period value '{period_val}' found for {symbol} enterprise value. Skipping record.")
         return None

    record = {
        'symbol': symbol,
        'date': api_data.get('date'),
        'period': period_val,
        'calendar_year': safe_int(api_data.get('calendarYear')),
        'stock_price': safe_decimal(api_data.get('stockPrice')),
        'number_of_shares': safe_int(api_data.get('numberOfShares')),
        'market_capitalization': safe_int(api_data.get('marketCapitalization')),
        'minus_cash_and_cash_equivalents': safe_int(api_data.get('minusCashAndCashEquivalents')),
        'add_total_debt': safe_int(api_data.get('addTotalDebt')),
        'enterprise_value': safe_int(api_data.get('enterpriseValue'))
    }
    return record

# 20. Insider Trades
def parse_insider_trade(api_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Parses FMP Insider Trading data into 'insider_trades' format."""
    if not api_data or not api_data.get('link'): # Use link as potential unique identifier
        logger.warning(f"Received incomplete insider trade data: {api_data}")
        return None

    record = {
        'symbol': api_data.get('symbol'),
        'filing_date': api_data.get('filingDate'),
        'transaction_date': api_data.get('transactionDate'),
        'reporting_cik': api_data.get('reportingCik'),
        'reporting_name': api_data.get('reportingName'),
        'issuer_cik': api_data.get('issuerCik'), # Check if FMP provides this
        'issuer_name': api_data.get('companyName'), # Assuming companyName is issuer
        'form_type': api_data.get('formType'), # e.g., '4'
        'securities_owned': safe_int(api_data.get('securitiesOwned')),
        'security_title': api_data.get('securityTitle'), # e.g., 'Common Stock'
        'transaction_type': api_data.get('type') or api_data.get('transactionCode'), # e.g., 'P', 'S'
        'price': safe_decimal(api_data.get('price') or api_data.get('transactionPrice')),
        'quantity': safe_int(api_data.get('quantity') or api_data.get('transactionShares')),
        'value': safe_int(api_data.get('totalValue') or api_data.get('value')), # Check FMP field name
        'acquired_disposed_code': api_data.get('acquistionOrDisposition'), # Check FMP field name ('A'/'D')
        'link': api_data.get('link')
    }
    return record

# 21. Political Disclosures
def parse_political_disclosure(api_data: Dict[str, Any], source: str) -> Optional[Dict[str, Any]]:
    """Parses FMP Senate/House disclosure data into 'political_disclosures' format."""
    if not api_data or not api_data.get('link'): # Link is unique key
        logger.warning(f"Received incomplete political disclosure data: {api_data}")
        return None

    record = {
        'source': source, # 'Senate' or 'House'
        'first_name': api_data.get('firstName'),
        'last_name': api_data.get('lastName'),
        'office': api_data.get('office'),
        'district': api_data.get('district'),
        'disclosure_date': api_data.get('disclosureDate'),
        'transaction_date': api_data.get('transactionDate'),
        'owner_type': api_data.get('owner'),
        'ticker': api_data.get('symbol') or api_data.get('ticker'), # FMP might use 'symbol'
        'asset_description': api_data.get('assetDescription'),
        'asset_type': api_data.get('assetType'),
        'transaction_type': api_data.get('type'), # e.g., 'Purchase', 'Sale'
        'amount_range': api_data.get('amount'),
        'capital_gains_over_200_usd': safe_bool(api_data.get('capitalGainsOver200USD')),
        'comment': api_data.get('comment'),
        'ptr_link': api_data.get('link')
    }
    return record

# 22. Stock Peers
def parse_stock_peers(api_data, symbol):
    """
    Normalises FMP stock‑peers payload into:
        { 'symbol': <focal>, 'peer_symbol': <peer>, 'last_fetched': datetime.utcnow() }
    Handles three payload shapes:
      • {'peersList': ['MSFT', …]}
      • ['MSFT', 'GOOG', …]
      • [{'symbol':'MSFT', ...}, {'symbol':'GOOG', ...}]
    """
    if isinstance(api_data, dict):
        peers_raw = api_data.get("peersList", [])
    elif isinstance(api_data, list):
        peers_raw = api_data
    else:
        logger.warning("Unexpected peers payload type %s for %s", type(api_data), symbol)
        return []

    now = datetime.utcnow().isoformat()
    rows = []
    for item in peers_raw:
        if isinstance(item, str):
            peer = item
        elif isinstance(item, dict) and "symbol" in item:
            peer = item["symbol"]
        else:
            logger.warning("Bad peer entry for %s: %r", symbol, item)
            continue
        rows.append({"symbol": symbol,
                     "peer_symbol": peer,
                     "last_fetched": now})
    return rows

# --- Example Usage ---
# Simulating the API response based on FMP documentation
# sample_api_response = [
#     {"symbol": "GPRO", "companyName": "GoPro, Inc.", "price": 0.9668, "mktCap": 152173717},
#     {"symbol": "MSFT", "companyName": "Microsoft Corporation", "price": 450.0, "mktCap": 3000000000000},
#     {"symbol": "GOOGL", "companyName": "Alphabet Inc.", "price": 180.0, "mktCap": 2000000000000}
# ]
# original_request_symbol = "AAPL"
#
# parsed_data = parse_stock_peers(sample_api_response, original_request_symbol)
# print(parsed_data)
# Expected Output:
# [
#   {'symbol': 'AAPL', 'peer_symbol': 'GPRO'},
#   {'symbol': 'AAPL', 'peer_symbol': 'MSFT'},
#   {'symbol': 'AAPL', 'peer_symbol': 'GOOGL'}
# ]

# # --- 23. DCF Valuations ------------------------------------------------------
 # pick up DCF field (try every variation you saw in your test output)
# unify list vs dict response
# fmp_fetcher/utils/parsing.py

def parse_dcf_valuation(api_data: Dict[str, Any], dcf_type: str) -> Optional[Dict[str, Any]]:
    """Parses FMP DCF data (/discounted-cash-flow, /levered-discounted-cash-flow)
    into 'dcf_valuations' format."""
    # FMP DCF endpoints usually return a list with one item, or a dict
    if isinstance(api_data, list):
        if not api_data:
            return None
        raw = api_data[0]
    elif isinstance(api_data, dict):
        raw = api_data
    else:
        logger.warning(f"Unexpected data type for DCF valuation: {type(api_data)}")
        return None

    # Must have symbol & date
    symbol = raw.get('symbol')
    dt = raw.get('date')
    if not symbol or not dt:
        logger.warning(f"Received incomplete DCF data: {raw}")
        return None

    # Try every variation of the DCF value field
    dcf_val = (
        raw.get("dcf")
        or raw.get("discountedCashFlow")
        or raw.get("discountedCashFlowValue")
    )
    # Try every variation of the stock price field
    price_val = (
        raw.get("Stock Price")
        or raw.get("stockPrice")
        or raw.get("StockPrice")
        or raw.get("stock_price")
    )

    return {
        'symbol':              symbol,
        'date':                dt,
        'dcf_type':            dcf_type,  # 'Standard' or 'Levered'
        'dcf_value':           safe_decimal(dcf_val),
        'stock_price_at_calc': safe_decimal(price_val)
    }


# 24. Institutional Ownership Summary
def parse_inst_ownership_summary(api_data: Dict[str, Any], symbol: str) -> Optional[Dict[str, Any]]:
    """Parses FMP positions summary data into 'institutional_ownership_summary' format."""
    if not api_data or not api_data.get('date'):
        logger.warning(f"Received incomplete Inst Ownership Summary for {symbol}: {api_data}")
        return None
    raw_date = api_data.get('date')
    if not raw_date:
        logger.warning(f"Missing date in Inst Ownership Summary for {symbol}: {api_data}")
        return None
    # Strip timezone Z and parse
    date_clean = raw_date.rstrip('Z')
    try:
        dt = datetime.fromisoformat(date_clean)
    except Exception:
        logger.warning(f"Invalid date format for Inst Ownership Summary for {symbol}: {raw_date}")
        return None
    date_iso = dt.date().isoformat()
    calendar_year = dt.year
    quarter = (dt.month - 1) // 3 + 1
    record = {
        'symbol': symbol,
        'cik': api_data.get('cik'),
        'date': date_iso,
        'calendar_year': calendar_year,
        'quarter': quarter,
        'investors_holding': safe_int(api_data.get('investorsHolding')),
        'investors_holding_change': safe_int(api_data.get('investorsHoldingChange')),
        'total_invested': safe_decimal(api_data.get('totalInvested')),
        'total_invested_change': safe_decimal(api_data.get('totalInvestedChange')),
        'ownership_percent': safe_decimal(api_data.get('ownershipPercent')),
        'new_positions': safe_int(api_data.get('newPositions')),
        'increased_positions': safe_int(api_data.get('increasedPositions')),
        'closed_positions': safe_int(api_data.get('closedPositions')),
        'decreased_positions': safe_int(api_data.get('reducedPositions')),
        'total_calls_invested': safe_decimal(api_data.get('totalCalls')),
        'total_puts_invested': safe_decimal(api_data.get('totalPuts'))
    }
    return record

# 25. Institutional Holdings Detail
def parse_inst_holding_detail(api_data: Dict[str, Any], symbol: str) -> Optional[Dict[str, Any]]:
    """Parses FMP filings extract analytics by holder into 'institutional_holdings' format."""
    if not api_data or not api_data.get('cik') or not api_data.get('date'):
        logger.warning(f"Received incomplete Inst Holding detail for {symbol}: {api_data}")
        return None
    raw_date = api_data.get('date')
    # Strip timezone Z if present
    date_clean = raw_date.rstrip('Z') if raw_date else None
    if not date_clean:
        logger.warning(f"Missing or invalid date for Inst Holding detail for {symbol}: {api_data}")
        return None
    try:
        dt = datetime.fromisoformat(date_clean)
    except Exception:
        logger.warning(f"Invalid date format for Inst Holding detail for {symbol}: {raw_date}")
        return None
    date_iso = dt.date().isoformat()
    calendar_year = dt.year
    quarter = (dt.month - 1) // 3 + 1
    record = {
        'symbol': symbol,
        'holder_cik': api_data.get('cik'),
        'holder_name': api_data.get('investorName') or api_data.get('holderName'),
        'date': date_iso,
        'calendar_year': calendar_year,
        'quarter': quarter,
        'shares_held': safe_int(api_data.get('sharesNumber')),
        'market_value': safe_decimal(api_data.get('marketValue')),
        'portfolio_weight': safe_decimal(api_data.get('weight')),
        'change_in_shares': safe_int(api_data.get('changeInSharesNumber')),
        'change_percentage': safe_decimal(api_data.get('changeInSharesNumberPercentage')),
        'filing_date': api_data.get('filingDate')
    }
    return record

# --- Press Release Parsing ---
def parse_press_release(api_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Parses a press release item from FMP API.
    
    Args:
        api_data: Raw API response data for a single press release
        
    Returns:
        Parsed press release ready for database insertion, or None if invalid
    """
    if not api_data or not isinstance(api_data, dict):
        logger.warning(f"Invalid press release data format: {api_data}")
        return None
    
    # Required fields - if any of these are missing, we skip the item
    required_fields = ['symbol', 'title', 'date']
    for field in required_fields:
        if field not in api_data or not api_data[field]:
            logger.warning(f"Press release missing required field: {field}")
            return None
    
    # Parse the item
    release_item = {
        'symbol': api_data.get('symbol'),
        'title': api_data.get('title'),
        'date': api_data.get('date'),
        'text': api_data.get('text', ''),
        'url': api_data.get('url', ''),
        'fetched_date': date.today().isoformat()
    }
    
    return release_item

# --- END ---