 import streamlit as st
  import pandas as pd
  import datetime

  # 1. CONFIGURATION
  SECTION_DB = {
      'C Channel': (0.40, 0.15),
      'Angle Iron': (0.65, 0.20),
      'U Channel': (0.80, 0.25),
      'I Beam': (1.20, 0.35),
  }

  # 2. SIDEBAR: SETTINGS & RATES
  with st.sidebar:
      st.title("📊 Settings")
      st.markdown("**Global Material Rates**")

      if 'rate_kg' not in st.session_state: st.session_state['rate_kg'] = 65.0
      if 'rate_paint' not in st.session_state: st.session_state['rate_paint'] = 45.0

      rate_kg = st.number_input("Steel Rate (THB/kg)",
                                value=st.session_state['rate_kg'],
                                min_value=0.0, format="%.2f")
      rate_paint = st.number_input("Paint Rate (THB/m2)",
                                   value=st.session_state['rate_paint'],
                                   min_value=0.0, format="%.2f")

      st.session_state['rate_kg'] = rate_kg
      st.session_state['rate_paint'] = rate_paint

      st.info("💡 Tip: Change rates anytime to see new totals.")

  # 3. INPUT SECTION: ADD ROWS
  col1, col2 = st.columns(2)

  with col1:
      st.markdown("**1. Section Details**")

      # Populate Selectbox
      options = list(SECTION_DB.keys()) + ['Custom / Other']
      selected_section = st.selectbox("Steel Section", options, index=0)

      # Retrieve properties
      if selected_section in SECTION_DB:
          weight_prop, surface_prop = SECTION_DB[selected_section]
          st.write(f"**Database Weight:** {weight_prop} kg/m | **Paint Area:** {surface_prop} m²/m")
      else:
          st.warning("Please enter custom values below.")
          weight_prop = st.number_input("Custom Weight (kg/m)", value=0.0, format="%.2f")
          surface_prop = st.number_input("Custom Surface (m2/m)", value=0.0, format="%.2f")

      qty = st.number_input("Quantity (Sets/pcs)", value=1, min_value=0, format="%d")
      length = st.number_input("Length (m)", value=1.0, min_value=0.0, format="%.2f")

  with col2:
      st.markdown("**2. Actions**")
      if st.button("➕ Add Row", use_container_width=True):
          # Prepare new row data
          new_row = pd.Series([
              selected_section,
              qty,
              length,
              weight_prop, # Store custom/db weight directly
              surface_prop, # Store custom/db surface directly
              0.0, 0.0, 0.0, 0.0, 0.0, # Calculated fields
              datetime.now().strftime("%Y-%m-%d")
          ], index=['Section', 'Quantity', 'Length', 'Weight', 'Surface',
                    'Total_Steel', 'Total_Paint', 'Total_Cost', 'Date'])

          # Append to session state
          st.session_state['steel_df'] = pd.concat([st.session_state['steel_df'], new_row], ignore_index=True)
          st.rerun()

  # 4. CALCULATION LOGIC
  def calculate_row(row, rate_kg, rate_paint):
      section_name = row['Section']
      qty = row['Quantity']
      length = row['Length']

      # Determine properties
      if section_name in SECTION_DB:
          w, s = SECTION_DB[section_name]
      else:
          # Custom Section logic
          w = row['Weight']
          s = row['Surface']

      # Calculate Metrics
      if qty > 0 and length > 0 and w > 0:
          calc_weight = qty * length * w
          calc_surface = calc_weight / w * s
          calc_cost = (calc_weight * rate_kg) + (calc_surface * rate_paint)

          row['Weight'] = calc_weight
          row['Surface'] = calc_surface
          row['Total_Steel'] = calc_weight * rate_kg
          row['Total_Paint'] = calc_surface * rate_paint
          row['Total_Cost'] = calc_cost
      else:
          # Handle zero quantities or invalid weights gracefully
          row['Weight'] = 0.0
          row['Surface'] = 0.0
          row['Total_Steel'] = 0.0
          row['Total_Paint'] = 0.0
          row['Total_Cost'] = 0.0

      return row

  # 5. DISPLAY RESULTS (TABLE)
  if 'steel_df' not in st.session_state:
      st.session_state['steel_df'] = pd.DataFrame(columns=['Section', 'Quantity', 'Length', 'Weight', 'Surface',
  'Total_Steel', 'Total_Paint', 'Total_Cost', 'Date'])

  if st.session_state['steel_df'].empty:
      st.write("⚠️ **No data entered yet.** Add steel sections in the left column.")
  else:
      st.markdown("---")
      st.header("📋 Bill of Materials (BOM) & Cost Estimate")

      # Apply current rates to all rows
      st.session_state['steel_df'] = st.session_state['steel_df'].apply(
          lambda row: calculate_row(row, st.session_state['rate_kg'], st.session_state['rate_paint'])
      )

      # Display formatted table
      df_display = st.session_state['steel_df'].copy()
      df_display['Total_Steel'] = df_display['Total_Steel'].apply(lambda x: f"{x:.2f} THB")
      df_display['Total_Paint'] = df_display['Total_Paint'].apply(lambda x: f"{x:.2f} THB")
      df_display['Total_Cost'] = df_display['Total_Cost'].apply(lambda x: f"{x:.2f} THB")

      st.dataframe(df_display, hide_index=True, use_container_width=True)
      st.info("💵 *Cost calculations update instantly when you change the sidebar rates.*")

  # 6. EXPORT DATA
  st.markdown("---")
  with st.expander("📤 Export Data"):
      csv_data = st.session_state['steel_df'].to_csv(index=False).encode('utf-8')
          row['Weight'] = 0.0
          row['Surface'] = 0.0
          row['Total_Steel'] = 0.0
          row['Total_Paint'] = 0.0
          row['Total_Cost'] = 0.0

      return row

  # 5. DISPLAY RESULTS (TABLE)
  if 'steel_df' not in st.session_state:
      st.session_state['steel_df'] = pd.DataFrame(columns=['Section', 'Quantity', 'Length', 'Weight', 'Surface',
  'Total_Steel', 'Total_Paint', 'Total_Cost', 'Date'])

  if st.session_state['steel_df'].empty:
      st.write("⚠️ **No data entered yet.** Add steel sections in the left column.")
  else:
      st.markdown("---")
      st.header("📋 Bill of Materials (BOM) & Cost Estimate")

      # Apply current rates to all rows
      st.session_state['steel_df'] = st.session_state['steel_df'].apply(
          lambda row: calculate_row(row, st.session_state['rate_kg'], st.session_state['rate_paint'])
      )

      # Display formatted table
      df_display = st.session_state['steel_df'].copy()
      df_display['Total_Steel'] = df_display['Total_Steel'].apply(lambda x: f"{x:.2f} THB")
      df_display['Total_Paint'] = df_display['Total_Paint'].apply(lambda x: f"{x:.2f} THB")
      df_display['Total_Cost'] = df_display['Total_Cost'].apply(lambda x: f"{x:.2f} THB")

      st.dataframe(df_display, hide_index=True, use_container_width=True)
      st.info("💵 *Cost calculations update instantly when you change the sidebar rates.*")

  # 6. EXPORT DATA
  st.markdown("---")
  with st.expander("📤 Export Data"):
      csv_data = st.session_state['steel_df'].to_csv(index=False).encode('utf-8')
      st.download_button(
          label="Download CSV",
          data=csv_data,
          file_name=f"steel_estimate_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.csv",
          mime="text/csv",
      )
