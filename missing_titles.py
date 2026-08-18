import streamlit as st
import pandas as pd

st.set_page_config(page_title="Missing Titles Finder", layout="centered")
st.title("Missing Titles Finder")

with st.expander("Instructions", expanded=True):
    st.markdown("""
1. **Download the Title Cabinet Excel file** from email.
2. **Download the Auction Run Report** from CATS for the particular auction date using the link below.
3. **Open the Auction Run Report**, copy the data, and paste it onto a new sheet in the Title Cabinet Excel file.
4. **Save the file** and upload it below to get the list of stock numbers with missing titles.
""")
    st.markdown("[Open Auction Run Report on CATS](https://cats.capitalautoauction.com/reports/customized/vehicles-summary?selected_report=&date_type=auctionAt&date_from=05%2F23%2F2026&date_to=05%2F23%2F2026&yard=&auctionType=&lane=&no_title=&isReleased=&stock_number_from=&stock_number_to=&arbitration=2&driver_assigned=&qb_check_printed=&charity_paid=&green_light=&title_status=&report_group=&quote_status=&pp_bid_id=&auto_offer_type_id=&priority_lead=&priority_second_lead=&has_tasks=&innovative_claims=&bidderSearchType=phone&bidderQuery=&is_avg_wear=&showPicture=0&showDocuments=0&removeCancelled=0&removeTitleChecked=0&removeSold=0&excludeDirectBuy=0&report_title=&available_fields%5B%5D=34&available_fields%5B%5D=124&available_fields%5B%5D=1&selected_fields%5B%5D=1&selected_fields%5B%5D=34&selected_fields%5B%5D=124&report_name=&report_format=web&report_range=&report_featured=0&report_id=)")

uploaded_file = st.file_uploader(
    "Upload the title cabinet file (Sheet1 = cabinet list, Sheet2 = auction run report)",
    type=["xlsx", "xls"],
)

if uploaded_file:
    try:
        # Sheet1: cabinet stock numbers, col A, no header
        df_cab = pd.read_excel(uploaded_file, sheet_name="Sheet1", header=None)
        titles_in_cabinet = set(df_cab[0].dropna().astype(str).str.strip())

        # Sheet2: auction run report — detect columns by name
        df_inv = pd.read_excel(uploaded_file, sheet_name="Sheet2", header=0)
        df_inv.columns = [c.strip() for c in df_inv.columns.astype(str)]

        col_map = {}
        for c in df_inv.columns:
            lc = c.lower()
            if "stock" in lc:
                col_map[c] = "StockNumber"
            elif "barcode" in lc:
                col_map[c] = "Barcode"
            elif "run" in lc:
                col_map[c] = "RunNumber"
            elif "yard" in lc:
                col_map[c] = "Yard"
        df_inv = df_inv.rename(columns=col_map)

        df_inv["StockNumber"] = df_inv["StockNumber"].astype(str).str.strip()
        df_inv["Barcode"]     = df_inv["Barcode"].astype(str).str.strip()
        df_inv["RunNumber"]   = df_inv["RunNumber"].astype(str).str.strip()

        has_yard = "Yard" in df_inv.columns
        if has_yard:
            df_inv["Yard"] = df_inv["Yard"].astype(str).str.strip()

        # Check 1: stock number in cabinet
        check_stock   = df_inv["StockNumber"].isin(titles_in_cabinet)
        # Check 2: barcode in cabinet
        check_barcode = df_inv["Barcode"].isin(titles_in_cabinet)

        both_no  = df_inv[~check_stock & ~check_barcode]
        non_mech = both_no[~both_no["RunNumber"].str.upper().str.startswith("MECH")]
        result   = non_mech.reset_index(drop=True)

        st.markdown("---")
        st.subheader(f"Missing Titles — {len(result)} record(s)")

        if result.empty:
            st.success("No missing titles found.")
        else:
            if has_yard:
                output_lines = []
                for yard, group in result.groupby("Yard"):
                    output_lines.append(yard)
                    output_lines.append("")
                    output_lines.extend(group["StockNumber"].tolist())
                    output_lines.append("")
                output_text = "\n".join(output_lines).strip()
            else:
                output_text = "\n".join(result["StockNumber"].tolist())

            st.caption("Copy to clipboard:")
            st.code(output_text, language=None)

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Upload the file above to see missing titles.")
