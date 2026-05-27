import streamlit as st
import pandas as pd

st.set_page_config(page_title="Missing Titles Finder", layout="centered")
st.title("Missing Titles Finder")

with st.expander("Instructions", expanded=True):
    st.markdown("""
1. **Download the Title Cabinet Excel file (BOX - MM/DD/YYYY)** from email.
2. **Download the Auction Run Report** from CATS for the particular auction date using the link below.
3. **Open the Auction Run Report**, copy the data, and paste it onto a new sheet in the Title Cabinet Excel file  (BOX - MM/DD/YYYY).
4. **Save the file** and upload it below to get the list of stock numbers with missing titles.
""")
    st.markdown("[Open Auction Run Report on CATS](https://cats.capitalautoauction.com/reports/customized/vehicles-summary?selected_report=&date_type=auctionAt&date_from=05%2F23%2F2026&date_to=05%2F23%2F2026&yard=&auctionType=&lane=&no_title=&isReleased=&stock_number_from=&stock_number_to=&arbitration=2&driver_assigned=&qb_check_printed=&charity_paid=&green_light=&title_status=&report_group=&quote_status=&pp_bid_id=&auto_offer_type_id=&priority_lead=&priority_second_lead=&has_tasks=&innovative_claims=&bidderSearchType=phone&bidderQuery=&is_avg_wear=&showPicture=0&showDocuments=0&removeCancelled=0&removeTitleChecked=0&removeSold=0&excludeDirectBuy=0&report_title=&available_fields%5B%5D=34&available_fields%5B%5D=124&available_fields%5B%5D=1&selected_fields%5B%5D=1&selected_fields%5B%5D=34&selected_fields%5B%5D=124&report_name=&report_format=web&report_range=&report_featured=0&report_id=)")

uploaded_file = st.file_uploader(
    "Upload the title cabinet file (Sheet1 = cabinet list, Sheet2 = inventory)",
    type=["xlsx", "xls"],
)

if uploaded_file:
    try:
        # Sheet1: cabinet stock numbers, col A, no header
        df_cab = pd.read_excel(uploaded_file, sheet_name="Sheet1", header=None)
        titles_in_cabinet = set(df_cab[0].dropna().astype(str).str.strip())

        # Sheet2: Stock Number, Barcode, Run Number (first row is header)
        df_inv = pd.read_excel(uploaded_file, sheet_name="Sheet2", header=0)
        df_inv.columns = ["StockNumber", "Barcode", "RunNumber"]

        df_inv["StockNumber"] = df_inv["StockNumber"].astype(str).str.strip()
        df_inv["Barcode"]     = df_inv["Barcode"].astype(str).str.strip()
        df_inv["RunNumber"]   = df_inv["RunNumber"].astype(str).str.strip()

        # Mirrors: =IF(COUNTIF(A:A, B2) > 0, "Yes", "No")
        check_stock   = df_inv["StockNumber"].isin(titles_in_cabinet)
        # Mirrors: =IF(COUNTIF(A:A, C2) > 0, "Yes", "No")
        check_barcode = df_inv["Barcode"].isin(titles_in_cabinet)

        # Keep only rows where both checks are "No"
        both_no  = df_inv[~check_stock & ~check_barcode]

        # Filter 2: exclude MECH run numbers
        non_mech = both_no[~both_no["RunNumber"].str.upper().str.startswith("MECH")]

        missing = non_mech

        result = missing[["StockNumber"]].reset_index(drop=True)

        st.markdown("---")
        st.subheader(f"Missing Titles — {len(result)} record(s)")

        if result.empty:
            st.success("No missing titles found.")
        else:

            st.caption("Copy to clipboard:")
            st.code("\n".join(result["StockNumber"].tolist()), language=None)

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Upload the file above to see missing titles.")
